import gzip
import shutil
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model

from .models import RegistroRespaldo


class RespaldoError(Exception):
    pass


def _db_path():
    cfg = settings.DATABASES['default']
    if cfg['ENGINE'] != 'django.db.backends.sqlite3':
        raise RespaldoError('Motor de BD no soportado todavía (solo SQLite).')
    return Path(cfg['NAME'])


def crear_respaldo(tipo, usuario=None):
    """Crea el respaldo comprimido y deja un RegistroRespaldo (exitoso o fallido)."""
    registro = RegistroRespaldo(tipo=tipo, usuario=usuario)
    try:
        carpeta = Path(settings.BACKUP_DIR)
        carpeta.mkdir(parents=True, exist_ok=True)
        # %f (microsegundos) evita que dos respaldos seguidos se llamen igual
        destino = carpeta / f'respaldo_{datetime.now():%Y%m%d_%H%M%S_%f}.sqlite3.gz'
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / 'copia.sqlite3'
            origen = sqlite3.connect(_db_path())
            dest = sqlite3.connect(copia)
            try:
                origen.backup(dest)       # copia consistente aunque la BD esté en uso
            finally:
                dest.close()
                origen.close()
            with open(copia, 'rb') as f_in, gzip.open(destino, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        registro.estado = 'exitoso'
        registro.ruta_archivo = str(destino)
        registro.tamano = destino.stat().st_size
    except Exception as exc:
        registro.estado = 'fallido'
        registro.detalle_error = str(exc)
    registro.save()
    return registro


def archivo_disponible(registro):
    """True si el archivo existe, está dentro de BACKUP_DIR y parece un .gz válido."""
    if registro.estado != 'exitoso' or not registro.ruta_archivo:
        return False
    ruta = Path(registro.ruta_archivo)
    try:
        if not ruta.resolve().is_relative_to(Path(settings.BACKUP_DIR).resolve()):
            return False
        if not ruta.is_file() or ruta.stat().st_size == 0:
            return False
        with open(ruta, 'rb') as f:
            return f.read(2) == b'\x1f\x8b'      # cabecera de gzip
    except OSError:
        return False


def restaurar_respaldo(registro, usuario=None):
    if not archivo_disponible(registro):
        raise RespaldoError('El archivo del respaldo no está disponible.')

    # Respaldo de seguridad del estado actual (G1-1009)
    previo = crear_respaldo('manual', usuario)
    if previo.estado != 'exitoso':
        raise RespaldoError(
            'No se pudo crear el respaldo previo; la restauración se canceló '
            'y no se hizo ningún cambio.'
        )

    # Foto del historial: al restaurar, la tabla vuelve al estado antiguo
    campos = ('fecha', 'tipo', 'estado', 'ruta_archivo', 'tamano', 'usuario_id', 'detalle_error')
    filas = list(RegistroRespaldo.objects.filter(estado='exitoso').values(*campos))

    try:
        with tempfile.TemporaryDirectory() as tmp:
            temporal = Path(tmp) / 'restaurar.sqlite3'
            with gzip.open(registro.ruta_archivo, 'rb') as f_in, open(temporal, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            origen = sqlite3.connect(temporal)
            try:
                if origen.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise RespaldoError('El respaldo está dañado; no se hizo ningún cambio.')
                destino = sqlite3.connect(_db_path())
                try:
                    origen.backup(destino)    # reemplaza el contenido actual
                finally:
                    destino.close()
            finally:
                origen.close()
    except (OSError, EOFError, sqlite3.DatabaseError) as exc:
        raise RespaldoError(f'No se pudo restaurar: {exc}') from exc

    # Volver a registrar los respaldos que la restauración "olvidó"
    User = get_user_model()
    existentes = set(RegistroRespaldo.objects.values_list('ruta_archivo', flat=True))
    for f in filas:
        if f['ruta_archivo'] in existentes:
            continue
        if f['usuario_id'] and not User.objects.filter(pk=f['usuario_id']).exists():
            f['usuario_id'] = None
        RegistroRespaldo.objects.create(**f)