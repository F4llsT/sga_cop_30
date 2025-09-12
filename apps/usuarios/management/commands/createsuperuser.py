from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.management import CommandError
from django.utils.text import capfirst
from django.db import DEFAULT_DB_ALIAS

class Command(BaseCommand):
    help = 'Used to create a superuser with a custom user model that includes a name field.'

    def handle(self, *args, **options):
        UserModel = self.UserModel
        database = options.get('database')

        try:
            if options.get('interactive'):
                # Same as original but with our custom logic
                # Get fields that need to be set
                field_names = ['email', 'nome']
                field_values = {}

                # Get each field, with a special case for password
                for field_name in field_names:
                    field = UserModel._meta.get_field(field_name)
                    user_value = None
                    input_msg = '%s: ' % field.verbose_name

                    # Handle different field types with appropriate input methods
                    if field.remote_field is None:
                        # Regular field
                        if field_name == 'email':
                            # Email validation
                            while user_value is None:
                                user_value = self.get_input_data(field, input_msg)
                                if not user_value:
                                    raise CommandError('Email não pode estar em branco.')
                                try:
                                    UserModel._default_manager.db_manager(database).get(email=user_value)
                                    self.stderr.write("Erro: Esse email já está em uso.")
                                    user_value = None
                                except UserModel.DoesNotExist:
                                    pass
                        else:
                            # For name field
                            while user_value is None:
                                user_value = self.get_input_data(field, input_msg)
                                if not user_value:
                                    raise CommandError('Nome não pode estar em branco.')
                    
                    field_values[field_name] = user_value

                # Get the password
                password = None
                while password is None:
                    password = self.get_password()
                
                # Create the user
                UserModel._default_manager.db_manager(database).create_superuser(
                    email=field_values['email'],
                    password=password,
                    nome=field_values['nome']
                )
                self.stdout.write("Superuser criado com sucesso!")
                
            else:
                # Non-interactive mode
                raise CommandError("É necessário executar em modo interativo.")
                
        except KeyboardInterrupt:
            self.stderr.write("\nOperação cancelada.")
            return

    def get_input_data(self, field, message, default=None):
        """
        Override this method if you want to customize data inputs or
        validation exceptions.
        """
        raw_value = input(message)
        if default and raw_value == '':
            raw_value = default
        try:
            val = field.clean(raw_value, None)
            return val
        except Exception as e:
            self.stderr.write("Erro: %s" % e)
            return None

    def get_password(self):
        """Get a password from the user."""
        from getpass import getpass
        while True:
            password = getpass()
            password2 = getpass('Password (again): ')
            if password != password2:
                self.stderr.write("Erro: Suas senhas não coincidem. Tente novamente.")
                continue
            if not password.strip():
                self.stderr.write("Erro: A senha não pode estar em branco.")
                continue
            return password
