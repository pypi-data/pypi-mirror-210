"""
Utilities for generating SQL to call APL procedures.
"""
from enum import Enum
from hana_ml.dataframe import quotename

class SqlGenerationMode(Enum):
    """
    Define how the sql queries will be generated, using Sql block, DU, with overview,...
    """
    UNDEFINED = None
    LEGACY = 0             # Procedure Any + With overview. Used in Hana2.
    SQLBLOCK_PROCANY = 1   # SQL Block + Procedure Any + No Overview. May be used Hana4 (never used till Feb 2023).
    SQLBLOCK_DU = 2        # SQL Block + DU. Used in Hana4.
    PROCEDURE_PROCANY = 3  # Temporal Procedure + Procedure Any + No Overview. May be used Hana4 with Hint for ECN purpose.

class AplSqlGenerator: #pylint: disable=too-many-instance-attributes
    """
    Utility class for the APL SQL block generation that will call an APL function.
    The generation takes care of the following mode (see enum SqlGenerationMode):
        SQLBLOCK_PROCANY = 1   # SQL Block + Procedure Any + No Overview. May be used Hana4 (never used till Feb 2023).
        SQLBLOCK_DU = 2        # SQL Block + DU. Used in Hana4 (never used till Feb 2023).
        PROCEDURE_PROCANY = 3  # Temporal Procedure + Procedure Any + No Overview. May be used Hana4 with Hint for ECN purpose.

    Examples of output:
    ------------------
    - Anonymous sql block using proc any (SqlGenerationMode.SQLBLOCK_PROCANY):
    DO (
            IN IN_FUNC_HEADER TABLE (KEY NVARCHAR(50), VALUE NVARCHAR(255))
            => #FUNC_HEADER_642345E1_29B0_4902_9D35_E91A865B0656_0,
            IN IN_GUESSVAR_CONFIG TABLE (KEY NVARCHAR(1000), VALUE NCLOB, CONTEXT NVARCHAR(100))
            => #GUESSVAR_CONFIG_642345E1_29B0_4902_9D35_E91A865B0656_0
        )
    BEGIN
        DECLARE OUT_MODEL TABLE(OID NVARCHAR(50), FORMAT NVARCHAR(50), LOB CLOB);
        DECLARE OUT_VARIABLE_DESC TABLE(RANK INT, NAME NVARCHAR(127), STORAGE NVARCHAR(10),
            VALUETYPE NVARCHAR(10), KEYLEVEL INT, ORDERLEVEL INT, MISSINGSTRING NVARCHAR(255),
            GROUPNAME NVARCHAR(255), DESCRIPTION NVARCHAR(255), OID NVARCHAR(50));
        IN_DATASET = select * from TRAIN_DATA_VIEW_642345E1_29B0_4902_9D35_E91A865B0656_0;
        CALL _SYS_AFL."APL_CREATE_MODEL"(
            -- Input
            :IN_FUNC_HEADER,
            :IN_GUESSVAR_CONFIG,
            :IN_DATASET,
            -- Output
            OUT_MODEL,
            OUT_VARIABLE_DESC
            );
        CREATE LOCAL TEMPORARY COLUMN TABLE "#GUESSVAR_MODEL_TRAIN_BIN_642345E1" as
            (select * from :OUT_MODEL);
        CREATE LOCAL TEMPORARY COLUMN TABLE "#VARIABLE_DESC_642345E1" as
            (select * from :OUT_VARIABLE_DESC);
    END;

    - Example of generated block sql for DU (SqlGenerationMode.SQLBLOCK_DU):
    DO (
        IN IN_FUNC_HEADER TABLE (KEY NVARCHAR(50), VALUE NVARCHAR(255))
        => #FUNC_HEADER_642345E1_29B0_4902_9D35_E91A865B0656_0,
        IN IN_GUESSVAR_CONFIG TABLE (KEY NVARCHAR(1000), VALUE NCLOB, CONTEXT NVARCHAR(100))
        => #GUESSVAR_CONFIG_642345E1_29B0_4902_9D35_E91A865B0656_0
    )
    BEGIN
        DECLARE OUT_MODEL TABLE(OID NVARCHAR(50), FORMAT NVARCHAR(50), LOB CLOB);
        DECLARE OUT_VARIABLE_DESC TABLE(RANK INT, NAME NVARCHAR(127), STORAGE NVARCHAR(10),
            VALUETYPE NVARCHAR(10), KEYLEVEL INT, ORDERLEVEL INT, MISSINGSTRING NVARCHAR(255),
            GROUPNAME NVARCHAR(255), DESCRIPTION NVARCHAR(255), OID NVARCHAR(50));
        DECLARE v_current_schema NVARCHAR(255);
        select current_schema into v_current_schema from dummy;

        CALL "SAP_PA_APL"."sap.pa.apl.base::CREATE_MODEL"(
            -- Input
            :IN_FUNC_HEADER,
            :IN_GUESSVAR_CONFIG,
            --:IN_DATASET,
            :v_current_schema,
            'TRAIN_DATA_VIEW_642345E1_29B0_4902_9D35_E91A865B0656_0',
            -- Output
            :OUT_MODEL,
            :OUT_VARIABLE_DESC
            );
        CREATE LOCAL TEMPORARY COLUMN TABLE "#GUESSVAR_MODEL_TRAIN_BIN_642345E1" as
            (select * from :OUT_MODEL);
        CREATE LOCAL TEMPORARY COLUMN TABLE "#VARIABLE_DESC_642345E1" as
            (select * from :OUT_VARIABLE_DESC);

    END;

    - The same for 'CREATE PROCEDURE' statement ((SqlGenerationMode.PROCEDURE_PROCANY))
    CREATE PROCEDURE xxxx (
        IN IN_FUNC_HEADER TABLE (KEY NVARCHAR(50), VALUE NVARCHAR(255)),
        IN IN_GUESSVAR_CONFIG TABLE (KEY NVARCHAR(1000), VALUE NCLOB, CONTEXT NVARCHAR(100))
    )
    LANGUAGE SQLSCRIPT AS
    BEGIN
        DECLARE OUT_MODEL TABLE(OID NVARCHAR(50), FORMAT NVARCHAR(50), LOB CLOB);
        DECLARE OUT_VARIABLE_DESC TABLE(RANK INT, NAME NVARCHAR(127), STORAGE NVARCHAR(10),
            VALUETYPE NVARCHAR(10), KEYLEVEL INT, ORDERLEVEL INT, MISSINGSTRING NVARCHAR(255),
            GROUPNAME NVARCHAR(255), DESCRIPTION NVARCHAR(255), OID NVARCHAR(50));
        IN_DATASET = select * from TRAIN_DATA_VIEW_642345E1_29B0_4902_9D35_E91A865B0656_0;
        CALL _SYS_AFL."APL_CREATE_MODEL"(
            -- Input
            :IN_FUNC_HEADER,
            :IN_GUESSVAR_CONFIG,
            :IN_DATASET,
            -- Output
            OUT_MODEL,
            OUT_VARIABLE_DESC
            );
        INSERT INTO "HANAML_GUESSVAR_MODEL_TRAIN_BIN_642345E1" as
            (select * from :OUT_MODEL);
        INSERT INTO "HANAML_VARIABLE_DESC_642345E1" as
            (select * from :OUT_VARIABLE_DESC);
    END;

    """
    def __init__(self, funcname, input_tables, output_tables, sql_generation_mode, new_procedure_name=None, with_hint=None):
        """
        Parameters
        ----------
        funcname : str
            The APL function name
        input_tables : list of str (a table name) or APLArtifactTable
            The input tables to be placed in the sql block
        output_tables : list of APLArtifactTable instances
            The output tables to be placed in the sql block
        sql_generation_mode: enum
            See enum SqlGenerationMode
        new_proc_name : str, optional
            The new procedure name
        with_hint: str optional
            If given, the sql will be ended with 'WITH HINT' clause. Only valid for 'PROCEDURE' case.
        """
        self.funcname = funcname
        self.input_tables = input_tables
        self.output_tables = output_tables
        self.sql_generation_mode = sql_generation_mode
        self.new_procedure_name = new_procedure_name
        self.with_hint = with_hint

        # Input variable names
        self.input_variables = [
            'IN_{}'.format(t) if isinstance(t, str) else 'IN_{}'.format(t.name)
            for t in input_tables]
        # Output table names
        self.output_tablenames = [t.name for t in output_tables]
        # Output variable names
        self.output_variables = ['OUT_{}'.format(t) for t in self.output_tablenames]

        if self.sql_generation_mode == SqlGenerationMode.PROCEDURE_PROCANY and not self.new_procedure_name:
            raise ValueError("Cannot generate APL SQL statement. The procedure name is not given.")

    def generate(self):
        """
        Generate a sql statement for APL function call.
        """
        if self.sql_generation_mode == SqlGenerationMode.SQLBLOCK_DU:
            return self._generate_du_block()
        if self.sql_generation_mode == SqlGenerationMode.SQLBLOCK_PROCANY:
            return self._generate_anonymous_block()
        if self.sql_generation_mode == SqlGenerationMode.PROCEDURE_PROCANY:
            return self._generate_create_procedure()
        raise ValueError("Cannot generate The APL DU SQL block statement. The specified generation mode is inconsistent.")

    def _generate_du_block(self):
        """
        Generate the sql statement for DU (Delivey Unit).

        Returns:
        --------
            A string
        """
        if self.sql_generation_mode != SqlGenerationMode.SQLBLOCK_DU:
            raise ValueError("Cannot generate The APL DU SQL block statement. The specified generation mode is inconsistent.")
        final_sql = '\n'.join([
            'DO (',
            '{declare_in_vars}',
            ')',
            'BEGIN',
            '{declare_out_vars}',
            '{v_current_schema}',
            '{call_statement}',
            '{create_tmp_tables}',
            'END;'
        ])
        # Builds sub-blocks
        declare_in_vars = self._sqlblock_declare_in_vars()
        v_current_schema = '\n'.join(['DECLARE v_current_schema NVARCHAR(255);',
                                      'select current_schema into v_current_schema from dummy;'])
        declare_out_vars = self._sqlblock_declare_out_vars()
        call_statement = self._sqlblock_call_statement_du()
        create_tmp_tables = self._sqlblock_create_tmp_tables()
        # Final assembly
        final_sql = final_sql.format(
            declare_in_vars=declare_in_vars,
            declare_out_vars=declare_out_vars,
            v_current_schema=v_current_schema,
            call_statement=call_statement,
            create_tmp_tables=create_tmp_tables
        )
        return final_sql

    def _generate_anonymous_block(self):
        """
        Generate the sql statement of anynomous block.

        Returns:
        --------
            A string
        """
        if self.sql_generation_mode != SqlGenerationMode.SQLBLOCK_PROCANY:
            raise ValueError("Cannot generate The APL anonymous SQL block statement. The specified generation mode is inconsistent.")

        # Decompose the SQL block into sub-blocks
        final_sql = '\n'.join([
            'DO (',
            '{declare_in_vars}',
            ')',
            'BEGIN',
            '{declare_out_vars}',
            '{declare_in_as_select}',
            '{call_statement}',
            '{create_tmp_tables}',
            'END;'
        ])

        # Build the sub-blocks
        # Builds {declare_in_vars}
        declare_in_vars = self._sqlblock_declare_in_vars()

        # Declares output variables: {declare_out_vars}
        declare_out_vars = self._sqlblock_declare_out_vars()

        # Builds {declare_in_as_select}
        declare_in_as_select = self._sqlblock_declare_in_as_select()

        # Call procedure statement: {call_statement}
        call_statement = self._sqlblock_call_statement_procany()

        # Insert output variables back to output tables
        create_tmp_tables = self._sqlblock_create_tmp_tables()

        # Final assembly
        final_sql = final_sql.format(
            declare_in_vars=declare_in_vars,
            declare_out_vars=declare_out_vars,
            declare_in_as_select=declare_in_as_select,
            call_statement=call_statement,
            create_tmp_tables=create_tmp_tables
        )
        return final_sql

    def _generate_create_procedure(self):
        """
        Generate the sql statement for procedure creation.

        Returns:
        --------
            A string
        """
        if self.sql_generation_mode != SqlGenerationMode.PROCEDURE_PROCANY:
            raise ValueError("Cannot generate the APL 'CREATE PROCEDURE' statement. The specified generation mode is inconsistent.")
        # Decompose the SQL block into sub-blocks
        sql_create_proc = '\n'.join([
            'CREATE PROCEDURE {new_proc_name} (',
            '{declare_in_vars}',
            ')',
            'LANGUAGE SQLSCRIPT AS',
            'BEGIN',
            '{declare_out_vars}',
            '{declare_in_as_select}',
            '{call_statement}',
            '{insert_output_tables}',
            'END;'
        ])

        # Build the sub-blocks

        # Builds {declare_in_vars}
        declare_in_vars = self._sqlblock_declare_in_vars()

        # Declares output variables: {declare_out_vars}
        declare_out_vars = self._sqlblock_declare_out_vars()

        # Builds {declare_in_as_select}
        declare_in_as_select = self._sqlblock_declare_in_as_select()

        # Call procedure statement: {call_statement}
        call_statement = self._sqlblock_call_statement_procany()

        # Insert output variables back to output tables
        insert_output_tables = self._sqlblock_insert_output_tables()

        # Final assembly for create procedure sql
        sql_create_proc = sql_create_proc.format(
            new_proc_name=self.new_procedure_name,
            declare_in_vars=declare_in_vars,
            declare_out_vars=declare_out_vars,
            declare_in_as_select=declare_in_as_select,
            call_statement=call_statement,
            insert_output_tables=insert_output_tables
        )
        return sql_create_proc

    def generate_call_procedure(self):
        """
        Generate the sql statement for procedure call.

        Parameters:
        ----------

        Returns:
        --------
            A string
        """
        if self.sql_generation_mode != SqlGenerationMode.PROCEDURE_PROCANY:
            raise ValueError("Cannot generate the APL 'CALL PROCEDURE' statement. The specified generation mode is inconsistent.")
        input_table_names = [t.name for t in self.input_tables if not isinstance(t, str)]
        input_table_names = ",".join(input_table_names)
        sql_call_proc = "CALL {new_proc_name} ({input_table_names})".format(
            new_proc_name=self.new_procedure_name,
            input_table_names=input_table_names
            )
        if self.with_hint:
            sql_call_proc = sql_call_proc + ' WITH HINT (' + self.with_hint + ')'

        return sql_call_proc

    def generate_drop_procedure(self):
        """
        Generate the sql statement for drop procedure.
        Returns:
        --------
            A string
        """
        if self.sql_generation_mode != SqlGenerationMode.PROCEDURE_PROCANY:
            raise ValueError("Cannot generate the APL 'DROP PROCEDURE' statement. The specified generation mode is inconsistent.")
        sql_drop_proc = "DROP PROCEDURE {new_proc_name}".format(
            new_proc_name=self.new_procedure_name
            )
        return sql_drop_proc

    def _sqlblock_declare_in_vars(self):
        """
        Build the declaration block {declare_in_vars} in the SQL block.
        See APLBase._call_apl_without_overview_procany

        Returns:
        --------
            A string
        """
        # Declares input the variables mapped to artifacts tables (APLArtifactTable)
        # Because those tables are local temporary tables, we cannot map them as:
        # <var_name> = select * from <table_name>;
        # within the block sql.
        lines = []
        for input_var, input_table in zip(self.input_variables, self.input_tables):
            if not isinstance(input_table, str):
                # "=> {input_table_name}" to be concatenated if anonymous block (no neeeded if procedure)
                arrow = '=> {input_table_name}'.format(input_table_name=input_table.name) \
                    if self.sql_generation_mode != SqlGenerationMode.PROCEDURE_PROCANY \
                    else ''
                line = 'IN {input_var} TABLE {table_def} {arrow}'.format(
                    input_var=input_var,
                    table_def=input_table.get_table_definition(),
                    arrow=arrow)
                lines.append(line)
        declare_in_vars = ',\n'.join(lines)
        return declare_in_vars

    def _sqlblock_declare_out_vars(self):
        """
        Build the declaration block {declare_out_vars} in the SQL block.
        See _call_apl_without_overview_procany
        Returns:
        --------
            A string
        """
        declare_out_vars = '\n'.join([
            'DECLARE {output_var} TABLE {table_def};'.format(
                output_var=output_var,
                table_def=output_table.get_table_definition()
            )
            for output_var, output_table in zip(self.output_variables, self.output_tables)
        ])
        return declare_out_vars

    def _sqlblock_declare_in_as_select(self):
        """
        Build the {declare_in_as_select} block in the SQL block.
        See _call_apl_without_overview_procany
        If the input table is given as a string (that is the case for the dataset table),
        we can't define them in {declare_in_vars} because we don't know its table-definition.
        We declare it inside the block sql as: <var_name> = select * from <table>;
        Returns:
        --------
            A string
        """
        declare_in_as_select = '\n'.join(
            ['{input_var} = select * from {input_table} ;'.format(
                input_var=input_var,
                input_table=input_table)
                for input_var, input_table in zip(self.input_variables, self.input_tables) \
                if isinstance(input_table, str)
            ]
        )
        return declare_in_as_select

    def _sqlblock_call_statement_procany(self):
        """
        Build the {call_statement} block in the SQL block. Using Procedure ANY (not DU)
        See _call_apl_without_overview_procany
        Returns:
        --------
            A string
        """
        call_statement = 'CALL _SYS_AFL.{}('.format(quotename(self.funcname))
        input_args = [':{}'.format(v) for v in ['{}'.format(v) for v in self.input_variables]]
        output_args = ['{}'.format(v) for v in self.output_variables]
        call_statement = call_statement + ', '.join([*input_args, *output_args]) + ');'
        return call_statement

    def _sqlblock_call_statement_du(self):
        """
        Builds the {call_statement} block using DU (not Procedure Any).
        Returns:
        -------
            A string

        """

        # Converts ANY procedure name to DU proc name (just remove the prefix APL_)
        if self.funcname == 'APL_AREA_PING_PROC':
            du_funcname = 'PING'
        else:
            du_funcname = self.funcname.replace('APL_', '')
        call_statement = 'CALL SAP_PA_APL."sap.pa.apl.base::{}"('.format(du_funcname)

        # input arguments
        input_args = []
        for input_var, input_table in zip(self.input_variables, self.input_tables):
            if not isinstance(input_table, str):
                # artifact tables
                input_args.append(':{}'.format(input_var))
            else:
                # If a table name (input dataset) is given, add current schema
                input_args.append(':v_current_schema')
                input_args.append("'{}'".format(input_table))
        #input_args = ', '.join(input_args)

        # output arguments
        # output_args = ', '.join([':{}'.format(v) for v in output_variables])
        output_args = []
        for output_var, output_table in zip(self.output_variables, self.output_tables):
            if isinstance(output_table, str):
                output_args.append(':v_current_schema')
                output_args.append(':{}'.format(output_var))
            else:
                output_args.append(':{}'.format(output_var))
        #output_args = ', '.join(output_args)

        # Call procedure statement
        call_statement = call_statement + ', '.join(input_args + output_args) + ');'
        return call_statement

    def _sqlblock_create_tmp_tables(self):
        """
        Build the {create_tmp_tables} block in the SQL block.
        See _call_apl_without_overview_procany
        Returns:
        --------
            A string
        """
        create_tmp_tables = '\n'.join([
            'CREATE LOCAL TEMPORARY TABLE {table_name} as (SELECT * FROM :{var_name});'.format(
                table_name=table_name,
                var_name=var_name)
            for table_name, var_name in zip(self.output_tablenames, self.output_variables)
        ])
        return create_tmp_tables

    def _sqlblock_insert_output_tables(self):
        """
        Build the {insert_output_tables} block in the SQL block.
        See _call_apl_without_overview_procany
        Returns:
        --------
            A string
        """
        create_tmp_tables = '\n'.join([
            'INSERT INTO {table_name} (SELECT * FROM :{var_name});'.format(
                table_name=table_name,
                var_name=var_name)
            for table_name, var_name in zip(self.output_tablenames, self.output_variables)
        ])
        return create_tmp_tables
