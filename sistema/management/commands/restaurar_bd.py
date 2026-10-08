from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from sistema.models import RegistroRespaldo
from sistema.respaldos import RespaldoError, restaurar_respaldo
from sistema.respaldos import crear_respaldo

class Command(BaseCommand):
    def handle(self, *args, **o):
        r = crear_respaldo('automatico')
        self.stdout.write(f'{r.estado}: {r.ruta_archivo or r.detalle_error}')


    def add_arguments(self, parser):
        parser.add_argument('ruta', help='Ruta del archivo .sqlite3.gz')
        parser.add_argument('--si', action='store_true', help='Confirmar sin preguntar')

    def handle(self, *args, **opciones):
        ruta = str(Path(opciones['ruta']).resolve())
        registro = RegistroRespaldo.objects.filter(ruta_archivo=ruta).first()
        if not registro:
            raise CommandError('Ese archivo no está registrado como respaldo.')
        if not opciones['si'] and input('Escribe RESTAURAR para continuar: ') != 'RESTAURAR':
            raise CommandError('Cancelado.')
        try:
            restaurar_respaldo(registro)
        except RespaldoError as exc:
            raise CommandError(str(exc))
        self.stdout.write(self.style.SUCCESS('Restauración completada.'))