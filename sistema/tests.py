import shutil
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings
from django.urls import reverse

from . import respaldos
from .models import RegistroRespaldo

User = get_user_model()


class BaseRespaldoTest(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

        self.db_falsa = self.tmp / 'falsa.sqlite3'
        con = sqlite3.connect(self.db_falsa)
        con.execute('CREATE TABLE t (valor TEXT)')
        con.execute("INSERT INTO t VALUES ('original')")
        con.commit()
        con.close()

        p = patch('sistema.respaldos._db_path', return_value=self.db_falsa)
        p.start()
        self.addCleanup(p.stop)
        o = override_settings(BACKUP_DIR=self.tmp / 'backups')
        o.enable()
        self.addCleanup(o.disable)

        self.admin = User.objects.create_user('admin', 'admin@t.com', 'Abc12345!')
        self.admin.user_permissions.add(Permission.objects.get(codename='gestionar_respaldos'))
        self.normal = User.objects.create_user('normal', 'normal@t.com', 'Abc12345!')

    def valor(self):
        con = sqlite3.connect(self.db_falsa)
        v = con.execute('SELECT valor FROM t').fetchone()[0]
        con.close()
        return v

    def cambiar(self, nuevo):
        con = sqlite3.connect(self.db_falsa)
        con.execute('UPDATE t SET valor = ?', (nuevo,))
        con.commit()
        con.close()


class AccesoTests(BaseRespaldoTest):
    def test_usuario_sin_permiso_recibe_403(self):
        r = respaldos.crear_respaldo('manual', self.admin)
        self.client.force_login(self.normal)
        self.assertEqual(self.client.get(reverse('respaldos_lista')).status_code, 403)
        self.assertEqual(self.client.post(reverse('respaldos_generar')).status_code, 403)
        self.assertEqual(self.client.get(reverse('respaldos_descargar', args=[r.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('respaldos_restaurar', args=[r.pk]),
        {'confirmacion': 'RESTAURAR'}).status_code, 403)
        self.assertEqual(RegistroRespaldo.objects.count(), 1)   # no se creó nada nuevo

    def test_anonimo_va_al_login(self):
        resp = self.client.get(reverse('respaldos_lista'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.url)


class GenerarTests(BaseRespaldoTest):
    def test_generar_manual_queda_registrado(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('respaldos_generar'))
        reg = RegistroRespaldo.objects.get()
        self.assertEqual(reg.tipo, 'manual')
        self.assertEqual(reg.estado, 'exitoso')
        self.assertEqual(reg.usuario, self.admin)
        self.assertTrue(Path(reg.ruta_archivo).is_file())


class DescargarTests(BaseRespaldoTest):
    def test_admin_descarga_archivo(self):
        r = respaldos.crear_respaldo('manual', self.admin)
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('respaldos_descargar', args=[r.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('attachment', resp['Content-Disposition'])
        self.assertTrue(b''.join(resp.streaming_content).startswith(b'\x1f\x8b'))
        resp.close()

    def test_archivo_inexistente_informa(self):
        r = respaldos.crear_respaldo('manual', self.admin)
        Path(r.ruta_archivo).unlink()
        self.client.force_login(self.admin)
        resp = self.client.get(reverse('respaldos_descargar', args=[r.pk]), follow=True)
        textos = [str(m) for m in resp.context['messages']]
        self.assertTrue(any('no está disponible' in t for t in textos))


class RestaurarTests(BaseRespaldoTest):
    def test_sin_confirmar_no_cambia_nada(self):
        r = respaldos.crear_respaldo('manual', self.admin)
        self.cambiar('cambiado')
        self.client.force_login(self.admin)
        self.client.post(reverse('respaldos_restaurar', args=[r.pk]), {'confirmacion': 'no'})
        self.assertEqual(self.valor(), 'cambiado')
        self.assertEqual(RegistroRespaldo.objects.count(), 1)

    def test_confirmado_restaura_y_crea_respaldo_previo(self):
        r = respaldos.crear_respaldo('manual', self.admin)
        self.cambiar('cambiado')
        self.client.force_login(self.admin)
        self.client.post(reverse('respaldos_restaurar', args=[r.pk]), {'confirmacion': 'RESTAURAR'})
        self.assertEqual(self.valor(), 'original')
        self.assertEqual(RegistroRespaldo.objects.filter(estado='exitoso').count(), 2)  # original + previo

    def test_si_falla_el_respaldo_previo_no_se_restaura(self):
        r = respaldos.crear_respaldo('manual', self.admin)
        self.cambiar('cambiado')
        fallido = RegistroRespaldo(tipo='manual', estado='fallido', detalle_error='x')
        with patch('sistema.respaldos.crear_respaldo', return_value=fallido):
            with self.assertRaises(respaldos.RespaldoError):
                respaldos.restaurar_respaldo(r, self.admin)
        self.assertEqual(self.valor(), 'cambiado')