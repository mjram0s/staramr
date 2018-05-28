"""
Classes for interacting with the (ResFinder/PointFinder) databases used to detect AMR genes.
"""
import argparse
import logging
import sys
from os import path, mkdir

from staramr.SubCommand import SubCommand
from staramr.Utils import get_string_with_spacing
from staramr.databases.AMRDatabasesManager import AMRDatabasesManager
from staramr.databases.resistance.ARGDrugTable import ARGDrugTable
from staramr.exceptions.CommandParseException import CommandParseException
from staramr.exceptions.DatabaseNotFoundException import DatabaseNotFoundException
from staramr.exceptions.DatabaseErrorException import DatabaseErrorException

"""
Base class for interacting with a database.
"""

logger = logging.getLogger('AMRDatabaseHandler')


class Database(SubCommand):

    def __init__(self, subparser, script_name):
        """
        Builds a SubCommand for interacting with databases.
        :param subparser: The subparser to use.  Generated from argparse.ArgumentParser.add_subparsers().
        :param script_name: The name of the script being run.
        """
        super().__init__(subparser, script_name)

    def _setup_args(self, arg_parser):
        arg_parser = self._subparser.add_parser('db', help='Download ResFinder/PointFinder databases')
        subparser = arg_parser.add_subparsers(dest='db_command',
                                              help='Subcommand for ResFinder/PointFinder databases.')

        Build(subparser, self._script_name + " db")
        Update(subparser, self._script_name + " db")
        Info(subparser, self._script_name + " db")
        RestoreDefault(subparser, self._script_name + " db")

        return arg_parser

    def run(self, args):
        super(Database, self).run(args)

        if args.db_command is None:
            self._root_arg_parser.print_help()


"""
Class for building a new database.
"""


class Build(Database):

    def __init__(self, subparser, script_name):
        """
        Creates a SubCommand for building a new database.
        :param subparser: The subparser to use.  Generated from argparse.ArgumentParser.add_subparsers().
        :param script_name: The name of the script being run.
        """
        super().__init__(subparser, script_name)

    def _setup_args(self, arg_parser):
        name = self._script_name
        self._default_dir = AMRDatabasesManager.get_default_database_directory()
        epilog = ("Example:\n"
                  "\t" + name + " build\n"
                                "\t\tBuilds a new ResFinder/PointFinder database under " + self._default_dir + " if it does not exist\n\n" +
                  "\t" + name + " build --dir databases\n" +
                  "\t\tBuilds a new ResFinder/PointFinder database under databases/")

        arg_parser = self._subparser.add_parser('build',
                                                epilog=epilog,
                                                formatter_class=argparse.RawTextHelpFormatter,
                                                help='Downloads and builds databases in the given directory.')
        arg_parser.add_argument('--dir', action='store', dest='destination', type=str,
                                help='The directory to download the databases into [' + self._default_dir + '].',
                                default=self._default_dir, required=False)
        arg_parser.add_argument('--resfinder-commit', action='store', dest='resfinder_commit', type=str,
                                help='The specific git commit for the resfinder database [latest].', required=False)
        arg_parser.add_argument('--pointfinder-commit', action='store', dest='pointfinder_commit', type=str,
                                help='The specific git commit for the pointfinder database [latest].', required=False)
        return arg_parser

    def run(self, args):
        super(Build, self).run(args)

        if path.exists(args.destination):
            if args.destination == self._default_dir:
                raise CommandParseException("Error, default destination [" + args.destination + "] already exists",
                                            self._root_arg_parser, print_help=True)
            else:
                raise CommandParseException("Error, destination [" + args.destination + "] already exists",
                                            self._root_arg_parser)
        else:
            mkdir(args.destination)

        if args.destination == AMRDatabasesManager.get_default_database_directory():
            database_handler = AMRDatabasesManager.create_default_manager().get_database_handler()
        else:
            database_handler = AMRDatabasesManager(args.destination).get_database_handler()
        database_handler.build(resfinder_commit=args.resfinder_commit, pointfinder_commit=args.pointfinder_commit)


"""
Class for updating an existing database.
"""


class Update(Database):

    def __init__(self, subparser, script_name):
        """
        Creates a SubCommand for updating an existing database.
        :param subparser: The subparser to use.  Generated from argparse.ArgumentParser.add_subparsers().
        :param script_name: The name of the script being run.
        """
        super().__init__(subparser, script_name)

    def _setup_args(self, arg_parser):
        self._default_dir = AMRDatabasesManager.get_default_database_directory()
        name = self._script_name
        epilog = ("Example:\n"
                  "\t" + name + " update databases/\n"
                                "\t\tUpdates the ResFinder/PointFinder database under databases/\n\n" +
                  "\t" + name + " update -d\n" +
                  "\t\tUpdates the default ResFinder/PointFinder database under " + self._default_dir)
        arg_parser = self._subparser.add_parser('update',
                                                epilog=epilog,
                                                formatter_class=argparse.RawTextHelpFormatter,
                                                help='Updates databases in the given directories.')

        arg_parser.add_argument('-d', '--update-default', action='store_true', dest='update_default',
                                help='Updates default database directory (' + self._default_dir + ').', required=False)
        arg_parser.add_argument('--resfinder-commit', action='store', dest='resfinder_commit', type=str,
                                help='The specific git commit for the resfinder database [latest].', required=False)
        arg_parser.add_argument('--pointfinder-commit', action='store', dest='pointfinder_commit', type=str,
                                help='The specific git commit for the pointfinder database [latest].', required=False)
        arg_parser.add_argument('directories', nargs='*')

        return arg_parser

    def run(self, args):
        super(Update, self).run(args)

        if len(args.directories) == 0:
            if not args.update_default:
                raise CommandParseException("Must pass at least one directory to update, or use '--update-default'",
                                            self._root_arg_parser,
                                            print_help=True)
            else:
                try:
                    database_handler = AMRDatabasesManager.create_default_manager().get_database_handler(
                        force_use_git=True)
                    database_handler.update(resfinder_commit=args.resfinder_commit,
                                            pointfinder_commit=args.pointfinder_commit)
                except DatabaseErrorException as e:
                    logger.error("Could not update default database. Please try restoring with 'staramr db restore'")
                    raise e
        else:
            for directory in args.directories:
                database_handler = AMRDatabasesManager(directory).get_database_handler()
                database_handler.update(resfinder_commit=args.resfinder_commit,
                                        pointfinder_commit=args.pointfinder_commit)


"""
Class for restoring the default database.
"""


class RestoreDefault(Database):

    def __init__(self, subparser, script_name):
        """
        Creates a SubCommand for restoring to the default database.
        :param subparser: The subparser to use.  Generated from argparse.ArgumentParser.add_subparsers().
        :param script_name: The name of the script being run.
        """
        super().__init__(subparser, script_name)

    def _setup_args(self, arg_parser):
        name = self._script_name
        epilog = ("Example:\n"
                  "\t" + name + " restore/\n"
                                "\t\tRestores the default ResFinder/PointFinder database\n\n")
        arg_parser = self._subparser.add_parser('restore',
                                                epilog=epilog,
                                                formatter_class=argparse.RawTextHelpFormatter,
                                                help='Restores the default ResFinder/PointFinder databases.')

        arg_parser.add_argument('-f', '--force', action='store_true', dest='force',
                                help='Force restore without asking for confirmation.', required=False)
        return arg_parser

    def _confirm_restore(self):
        """
        Confirms with the user whether or not to restore the database directory.
        :return: True if should restore, False otherwise.
        """
        confirmed = False
        while not confirmed:
            response = str(input(
                "Restore the default ResFinder/PointFinder databases (Y/N)? ").lower().strip())
            if response == 'y' or response == 'yes':
                return True
            elif response == 'n' or response == 'no':
                return False

    def run(self, args):
        super(RestoreDefault, self).run(args)

        database_manager = AMRDatabasesManager.create_default_manager()

        if not args.force:
            response = self._confirm_restore()
        else:
            response = True

        if response:
            database_manager.restore_default()


"""
Class for getting information from an existing database.
"""


class Info(Database):

    def __init__(self, subparser, script_name):
        """
        Creates a SubCommand for printing information about a database.
        :param subparser: The subparser to use.  Generated from argparse.ArgumentParser.add_subparsers().
        :param script_dir: The directory containing the main application script.
        :param script_name: The name of the script being run.
        """
        super().__init__(subparser, script_name)

    def _setup_args(self, arg_parser):
        name = self._script_name
        default_dir = AMRDatabasesManager.get_default_database_directory()
        epilog = ("Example:\n"
                  "\t" + name + " info\n"
                                "\t\tPrints information about the default database in " + default_dir + "\n\n" +
                  "\t" + name + " info databases\n" +
                  "\t\tPrints information on the database stored in databases/")
        arg_parser = self._subparser.add_parser('info',
                                                epilog=epilog,
                                                formatter_class=argparse.RawTextHelpFormatter,
                                                help='Prints information on databases in the given directories.')
        arg_parser.add_argument('directories', nargs='*')

        return arg_parser

    def run(self, args):
        super(Info, self).run(args)

        arg_drug_table = ARGDrugTable()

        if len(args.directories) == 0:
            database_handler = AMRDatabasesManager.create_default_manager().get_database_handler()

            try:
                database_info = database_handler.info()
                database_info.extend(arg_drug_table.get_resistance_table_info())
                sys.stdout.write(get_string_with_spacing(database_info))
            except DatabaseNotFoundException as e:
                logger.error("No database found. Perhaps try restoring the default with 'staramr db restore'")
        else:
            for directory in args.directories:
                try:
                    database_handler = AMRDatabasesManager(directory).get_database_handler()
                    database_info = database_handler.info()
                    database_info.extend(arg_drug_table.get_resistance_table_info())
                    sys.stdout.write(get_string_with_spacing(database_info))
                except DatabaseNotFoundException as e:
                    logger.error(
                        'Database not found in [' + directory + "]. Perhaps try building with 'staramr db build --dir " + directory + "'")
