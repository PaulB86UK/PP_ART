/****** Object:  UserDefinedFunction [DPCBG].[Get_JSONTableMapping]    Script Date: 08/12/2022 08:57:03 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE FUNCTION [DPCBG].[Get_JSONTableMapping](@TableName VARCHAR(250))
RETURNS TABLE
AS
RETURN
SELECT jsonmapping = '{"type": "TabularTranslator", "mappings": ' + 
(
    SELECT
         'source.path'  = '[''' + IIF(c.[name] = 'Guid','GUID_regel',c.[name]) + ''']'
  --      ,'source.type'  = m.ADFTypeDataType
        ,'sink.name'    = c.[name]
        ,'sink.type'    = m.ADFTypeDataType
    FROM sys.tables                 t
    JOIN sys.schemas                s ON s.schema_id        = t.schema_id
    JOIN sys.all_columns            c ON c.object_id        = t.object_id
    JOIN sys.types                  y ON c.system_type_id   = y.system_type_id
                                        AND c.user_type_id  = y.user_type_id
    JOIN [DPCBG].[ADF_To_SQL_Type_Mappings]    m ON y.[name]           = m.SQLServerDataType
    WHERE   1 = 1
        AND t.[name] = @TableName
        AND s.[name] = 'DPCBG'
    ORDER BY c.column_id
    FOR JSON PATH
) + ',"mapComplexValuesToString": true}';
GO
