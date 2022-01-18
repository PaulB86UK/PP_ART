###################################################################
## pySQL Translation of the SPSS Modeller Friday AM Pack TOW Stream
## Author: Pablo Puente
## Created Date:  25/0/2021
## Last Modified: 31/08/2021
## Version : 2
###################################################################
# List of Changes:
#-Added Fix pySQL Code. Added controls, fix logs, and exceptions.
#-Added Empty Tables Control. Fix SQL Connection
#
###################################################################


#LIBRARIES
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import logging
    import datetime
    from datetime import date
    logging.basicConfig(filename= f'C:\Logfiles\Clean Below Ground SPSS to SQL Friday AM Pack Tow {date.today()}.log', level = logging.DEBUG)
    import sys
    import subprocess
    import pkg_resources
    
    
    now = datetime.datetime.now()
except Exception as e:
    logging.error(e, exc_info=True)

required = {'pandasql'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    logging.info(f'{missing} attempting install')
    python = sys.executable
    try:
        now = datetime.datetime.now()
        subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
        logging.info(f'{now} Missing Libraries Installed')
    except Exception as e:
        logging.error(e, exc_info=True)

try:
    from time import sleep
    import getpass
    import os
    import pandas as pd
    import sqlalchemy as db
    import subprocess
    import urllib
    import keyring
    import sys
    import numpy as np
    import sys
    import pyodbc
    from pandasql import sqldf
    now = datetime.datetime.now()
    logging.info(f'{now} Libraries Loaded')
except Exception as e:
        logging.error(e, exc_info=True)



#METHODS
def Fix_from_SQL(df):
    COUNT = 0
    for TIEMPO in ['YTD','Weekly']:
        for ZONA in list(df.Region.value_counts().index):
            query =  f"""
            SELECT 		[Split NM MCO] as 'Split'
                    ,	SUM([Total Operations]) AS '{TIEMPO} {ZONA}'
            FROM df
            WHERE REGION = '{ZONA}'	AND FLAG = '{TIEMPO}'
            GROUP BY [Split NM MCO], [Region]

            UNION

            SELECT 		[Split CUSDR] as 'Split'
                    ,	SUM([Total Operations]) AS '{TIEMPO} {ZONA}'
            FROM df
            WHERE REGION = '{ZONA}'	AND FLAG = '{TIEMPO}'
            GROUP BY [Split CUSDR] 

            UNION

            SELECT		[Split NM] AS 'Split'
                    ,	SUM([Total Operations]) AS '{TIEMPO} {ZONA}'
            FROM df
            WHERE REGION = '{ZONA}' AND FLAG = '{TIEMPO}' AND [Split NM] != 'NULL'
            GROUP BY [Split NM]
            """
            if COUNT == 0:
                output = sqldf(query)
            if COUNT > 0:
                output = output.merge(sqldf(query),how = 'left', on= 'Split')
            COUNT += 1
    YTD_COLUMNS = ['YTD North London', 'YTD South London', 'YTD Thames Valley']
    WEEKLY_COLUMNS = ['Weekly North London', 'Weekly South London', 'Weekly Thames Valley']
    output['YTD Thames Water'] = output[YTD_COLUMNS].sum(axis =1)
    output['Weekly Thames Water'] = output[WEEKLY_COLUMNS].sum(axis =1)
    #reordewr
    output = output[['Split','Weekly Thames Water','Weekly North London', 'Weekly South London', 'Weekly Thames Valley','YTD Thames Water','YTD North London', 'YTD South London', 'YTD Thames Valley',]]
    output = output.reindex([1,6,3,2,7,4,0,8,9,10,11,12,13,14])

    return output
    
##############################
#SQL CONFIGURATION AND LOGFILE
##############################




user = os.getlogin()
logging.info(f'{now} - user : {user}')

user_username = None
user_password = None

if user == 'AAndreou':
    user_username = 'aandreou.scripts'
    user_password = 'AntoniaSQLpass'
elif user == 'PLAKER':
    user_username = 'plaker.scripts'
    user_password = 'plakerSQLpass'    
elif user == 'PPuente':
    user_username = 'PPuente.scripts'  
    user_password = 'pp_keyring'
elif user == 'JLong2':
    user_username = 'jlong2.scripts'  
    user_password = 'jl_keyring'

elif user == 'OAina':
    user_username = 'oaina.scripts'  
    user_password = 'oa_keyring'


else:
    print('\n User not set up!')
    user_username = input('SQL Scripts Username: ')
    print('Input SQL scripts password')
    user_password = getpass.getpass()
    keyring_user_name = "'" + user + "SQLpass'"
    keyring.set_password(keyring_user_name,user_username, user_password)
    user_password = keyring_user_name
    print(f"You are now set up on and your keyring user name is {keyring_user_name}. Record it and ask to be added as a routine user on the code!")

username = user_username
password = keyring.get_password(user_password, user_username)

server='sql-ne-high-opswastecfs-prod.database.windows.net'
database='sqldb-high-opswastecfs-prod'
driver='{ODBC Driver 17 for SQL Server}'
params = urllib.parse.quote_plus("DRIVER=" + driver + ";SERVER=" + server + ";DATABASE=" + database + ";UID=" + username + ";PWD=" + password)

engine = db.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params, module=pyodbc, pool_size=10, max_overflow=20, fast_executemany=True)

connection = engine.raw_connection()
cursor = connection.cursor() 
now = datetime.datetime.now()
logging.info(f'{now} - Day of Week - {date.today().weekday()}')
#Start the ZHR_EMP_TIME_Report Consolidation and Upload to SQL 

#print("Checking Day of the Week")
#if date.today().weekday() == 2:  RESTORE WHEN TESTING DONE (THURSDAY (3))
    #print("Today is Friday")


###########
#SQL QUERY#
###########

## FRIDAY AM PACK FIX
######################
now = datetime.datetime.now()
logging.info(f'{now} - Starting Friday Am Pack Fix.') 
QRY_FIX = pd.read_sql_query(
'''
WITH BASE AS (
				SELECT		opr_operation_number_key						AS 'OPR_Operation Number - Key'
						,	opr_standard_text_key_zcktsch_key				AS 'OPR_Standard Text Key (ZCKTSCH) - Key'
						,	lead_order										AS 'Lead Order'
						,	opr_actual_operation_type_key					AS 'OPR_Actual OperationType - Key'
						,	opr_work_center_area_medium_text				AS 'OPR_Work Center Area - Medium Text'
						,	region											AS 'Region'
						,	opr_operation_actual_end_time					AS 'OPR_Operation Actual End Time'
						,	total_operations								AS 'Total Operations'
						,	opr_op_dispatch_date							AS 'OPR_OP Dispatch Date'
						,	opr_op_dispatch_time							AS 'OPR_OP Dispatch Time'
						,	opr_operation_number_system_conditon_key		AS 'OPR_Operation Number - System Conditon (Key)'
						,	opr_op_crtd_date								AS 'OPR_OP CRTD Date'
						,	opr_operation_actual_end_date					AS 'OPR_Operation Actual End Date'
						,	opr_operation_first_time_in_progress_date_key	AS 'OPR_Operation First Time In Progress Date - Key'
						,	opr_operation_first_time_in_progress_time_key	AS 'OPR_Operation First Time In Progress Time - Key'
						,	opr_operation_number_cancelled_key				AS 'OPR_Operation Number - Cancelled (Key)'
						,	op_number_short									AS 'Op Number (Short)'
						,	ord_maint_activity_type_key						AS 'ORD_Maint. Activity Type - Key'
						,	ord_work_order_number_room_key					AS 'ORD_Work Order Number - Room (Key)'
						,	stk_category									AS 'STK Category'
						,	mco												AS 'MCO'
						,	stk_subcategory									AS 'STK Sub-Category'
						,	aot_category									AS 'AOT Category'
						,	mco_aot											AS 'MCO (AOT)'
						,	aot_subcategory									AS 'AOT Sub-Category'
						,	operation_created_datetime						AS 'Operation Created Date/Time'
						,	operation_unco_status_datetime					AS 'Operation UNCO Status Date/Time'
						,	operation_canc_datetime							AS 'Operation CANC Date/Time'
						,	operation_comp_status_datetime					AS 'Operation COMP Status Date/Time'
						,	operation_released_datetime						AS 'Operation Released Date/Time'
						,	first_in_progress_datetime						AS 'First In Progress Date/Time'
						,	activity_category_stk							AS 'Activity Category (STK)'
						,	lead_order_mat									AS 'Lead Order MAT'
						,	initial_journey_type							AS 'Initial Journey Type'
						,	flag_complete									AS 'Flag: Complete'
						,	flag_cancelled									AS 'Flag: Cancelled'
						,	flag_tow										AS	'Flag: TOW'
						,	age_operation_created							AS 'Age (Operation Created)'
						,	cycle_time_operation_created					AS 'Cycle Time (Operation Created)'
						,	time_to_attend									AS 'Time to Attend'
						,	flag_preplanned									AS 'Flag: Pre-Planned'
						,	flag_first_time_scheduled						AS 'Flag: First Time Scheduled'
						,	operation_created_to_released_time_mins			AS 'Operation Created to Released Time (mins)'
						,	flag_validation_compliance						AS 'Flag: Validation Compliance'
						,	promise_datetime								AS 'Promise Date/Time'
						,	promise_date									AS 'Promise Date'
						,	promise_compliance								AS 'Promise Compliance'
						,	flag_new_epoch									AS 'Flag: New Epoch'
						
						--Week Ending Node #10
						-----------------------
						,	CASE	WHEN DATEPART(WEEKDAY, opr_operation_actual_end_date) != 7 THEN
										DATEADD(d,6- DATEPART(weekday,opr_operation_actual_end_date), opr_operation_actual_end_date)
									WHEN DATEPART(WEEKDAY, opr_operation_actual_end_date) = 7 THEN
										DATEADD(d,-1 + DATEPART(weekday,opr_operation_actual_end_date),	opr_operation_actual_end_date)
									END			AS		'Week Ending'


				FROM	[dbo].[cbg_cdm_output_operations]
				WHERE 
						[opr_operation_number_work_centre_text] LIKE	('%Water R&M%')			--First Node
				AND		opr_control_key_key						=		'PM03'					--Second Node
				AND		[stk_category]							=		'Water Network R&M'		--3rd Node
				AND		(mco									!=		'NA'	
				OR 		mco										IS NOT NULL)					--3rd Node)

				AND		aot_category							=		'Water Network R&M'		--3rd Node
				AND		(mco_aot								!=		'NA'	
				OR  	 mco_aot								IS NOT NULL)					--3rd Node
								--3rd Node
				AND		[flag_complete]							=		1						--Node 5 Comp Only
				AND		[flag_cancelled]						=		0						--Node 5 Comp Only
				AND		ord_maint_activity_type_key				LIKE	('%NM%')				--Node 6 NM Only
		  

	
		  
				)	
				,
				
	BASE2 AS	(
				SELECT				[Total Operations]
								,	[OPR_Operation Actual End Date] AS 'Completed Date'
								,	[Week Ending]	
								,	CASE																		--4a Node
																					WHEN region in ('CN','EN')	THEN 'North London'
																					WHEN region in ('CS','ES')	THEN 'South London'
																					WHEN region =	'WE'		THEN 'Thames Valley'
																					ELSE 'NA'
									END AS	'Region'

									--Node #8: Triple Split : Part A NM
								,	CASE  
										WHEN	[ORD_Maint. Activity Type - Key]	='NM1'	THEN	'NM1 (Customer)'					
										WHEN	[ORD_Maint. Activity Type - Key]	='NM2'	THEN	'NM2 (H&S Customer)'				
										WHEN	[ORD_Maint. Activity Type - Key]	='NM3'	THEN	'NM3 (H&S Non-Customer)'			
										WHEN	[ORD_Maint. Activity Type - Key]	='NM4'	THEN	'NM4 (Leakage Enabling)'			
										WHEN	[ORD_Maint. Activity Type - Key]	='NM5'	THEN	'NM5 (Network Maintenance)'		
										WHEN	[ORD_Maint. Activity Type - Key]	='NM6'	THEN	'NM6 - (Water Quality - Customer)'
										WHEN	[ORD_Maint. Activity Type - Key]	='NM7'	THEN	'NM7 - (Water Quality - Lead Pipe)'
										ELSE														'NM - (Other)'
									END AS 'Split NM'

									--Node #8: Triple Split : Part B CUSDR / NON CUSDR
								,	CASE WHEN	[ORD_Maint. Activity Type - Key] IN ('NM1','NM2','NM6') THEN 'NM CUSDR' ELSE 'NM Non-CUSDR' END AS 'Split CUSDR'

									--Node #8: Triple Split : Part C NM MCO
								,	CASE WHEN	[MCO (AOT)] LIKE ('%N/L%')	THEN 'NM N/L' ELSE CONCAT('NM',' ',[MCO (AOT)]) END AS 'Split NM MCO'

				FROM BASE

				WHERE [Week Ending] < CAST(GETDATE() AS DATE) AND [Week Ending] > '2021-04-02'
				)
				,
	BASEYTD AS	(
				SELECT		Region
						,	[Split NM]
						,	[Split NM MCO]
						,	[Split CUSDR]
						,	COUNT([Total Operations]) AS 'Total Operations' 
						,	'YTD' AS 'FLAG'
				FROM BASE2
				GROUP BY Region, [Split NM],[Split NM MCO],[Split CUSDR]
				)
				,
	BASEWEEK AS	(
				SELECT		Region
						,	[Split NM]
						,	[Split NM MCO]
						,	[Split CUSDR]
						,	COUNT([Total Operations]) AS 'Total Operations' 
						,	'Weekly' AS 'FLAG'
				FROM BASE2
				WHERE DATEDIFF(DAY,[Week Ending],CAST(GETDATE() AS DATE)) <=7
				AND	  DATEDIFF(DAY,[Week Ending],CAST(GETDATE() AS DATE)) >=0
				GROUP BY Region, [Split NM],[Split NM MCO],[Split CUSDR]



				)

SELECT * FROM BASEYTD
UNION
SELECT * FROM BASEWEEK
;
''',engine)
now = datetime.datetime.now()
logging.info(f'{now} - Friday AM Pack SQL Code Run')  
QRY_FIX = Fix_from_SQL(QRY_FIX)

logging.info(f'{now} - Friday AM Pack Data Transformations succesful')
QRY_FIX.to_csv(r'C:\CBG Friday am Pack\PySQL Outputs\Report\CBG Friday Am Pack Fix.csv', index = False)
now = datetime.datetime.now()
logging.info(f'{now} - Friday AM Pack Fix Report File Created.')  


## FRIDAY AM PACK TOW
######################

### CSL ACTIVITIES TABLE

QRY_CSL_ACT_TABLE = pd.read_sql_query('''
    DECLARE @Fecha DATE;
    SET @Fecha = CAST(GETDATE() AS DATE);
    WITH SUBA AS	(
                    SELECT * FROM [dbo].[cbg_cdm_output_csl_activities]
                    WHERE flag_repair_activity = 1
                    )
                    ,

        SUBB AS		(
                    SELECT		[activity]												AS 'Detection Activity'
                            ,	CAST([activity_and_field_completion_date] AS DATE)		AS 'Detection Completion Date'
                    FROM [dbo].[cbg_cdm_output_csl_activities]
                    
                    )
                    ,

        SUBC AS	(
                    SELECT * 
                    FROM SUBA A
                    LEFT JOIN 
                    (SELECT * FROM SUBB) B
                    ON A.[detection_activity] =		B.[Detection Activity]
                    WHERE	Activity		  !=	'Detection Activity'
                                
                    )
                    ,

        BASE AS	(
                        SELECT		[process_number]
                                ,	[activity]												AS 'Activity'
                                ,	CAST([activity_and_field_completion_date] AS DATE)		AS 'Activity and field completion date'
                                ,	[Detection Activity]
                                ,	[Detection Completion Date]
                                ,	CASE	WHEN region in ('CN','EN')	THEN 'NL'
                                            WHEN region in ('CS','ES')	THEN 'SL'
                                            WHEN region =	'WE'		THEN 'TV'
                                            ELSE 'NA'
                                    END														AS 'Region'
                                ,	[flag_complete]
                                ,	[flag_outstanding]

                        FROM SUBC
                        WHERE			[flag_repair_activity]	=	1
                                AND		Activity				!=	'Detection Activity'
                                
                                
                        )
                        ,
        BASETW	AS		(
                        SELECT * FROM BASE
                    
                        UNION ALL
                        
                        SELECT		[process_number]
                                ,	[Activity]
                                ,	[Activity and field completion date]
                                ,	[Detection Activity]
                                ,	[Detection Completion Date]
                                ,	'TW' AS Region
                                ,	[flag_complete]
                                ,	[flag_outstanding]
                        FROM BASE
                        )
                        ,
        BASE2	AS		(
                        SELECT			process_number									AS	'Process Number'
                                    ,	Region
                                    ,	MIN([Detection Completion Date])				AS	'MIN Detection Completion Date'
                                    ,	MAX([Activity and field completion date])		AS	'MAX Detection Completion Date'
                                    ,	SUM([flag_outstanding])							AS	'SUM Flag: Outstanding'
                                    ,	SUM([flag_complete])							AS	'SUM Flag: Complete'

                        FROM BASETW	
                        
                        GROUP BY	process_number, Region
                        )
                        ,
        BASE3	AS		(
                        SELECT			*
                                    ,	DATEDIFF(DAY,[MIN Detection Completion Date],[MAX Detection Completion Date])	AS	'CSL Cycle Time'
                                    ,	CASE	WHEN DATEPART(WEEKDAY, [MAX Detection Completion Date]) != 7 THEN
                                                    DATEADD(d, 6 - DATEPART(WEEKDAY, [MAX Detection Completion Date]), [MAX Detection Completion Date])
                                                WHEN DATEPART(WEEKDAY, [MAX Detection Completion Date]) = 7 THEN
                                                    DATEADD(d, 6 ,	[MAX Detection Completion Date])
                                        END	AS 'Week Ending Date'
                        FROM BASE2
                        WHERE			[SUM Flag: Outstanding]	=	0
                                AND		[SUM Flag: Complete]	>	0
                                AND		[MIN Detection Completion Date] IS NOT NULL
                                --AND		[MIN Detection Completion Date] != ''

                        )
    SELECT		Region
            ,	'CSL Cycle Time'		AS 'Metric'
            ,	AVG([CSL Cycle Time])	AS 'Metric Value'
    FROM	BASE3
    WHERE		DATEDIFF(DAY,[Week Ending Date],@Fecha) <=7
            AND	DATEDIFF(DAY,[Week Ending Date],@Fecha) >=0 
    GROUP BY Region
    ;''',engine)
now = datetime.datetime.now()
logging.info(f'{now} - CSL Activities Table Query Succeed')
      

try:
    QRY_CSL_ACT_TABLE.to_csv(r'C:\CBG Friday am Pack\PySQL Outputs\Raw Files\CSL Activities Table.csv', index = False)
    now = datetime.datetime.now()
    logging.info(f'{now} - CSL Activities Table Query Run and Stored in CSV File.')   
except Exception as e:
        logging.error(e, exc_info=True)

### OPERATIONS OUTSTANDING TRACKER
QRY_OP_TOW_TRACK = pd.read_sql_query('''
DECLARE @Fecha DATE;
SET @Fecha = CAST(GETDATE() AS DATE);
WITH BASE	AS	(

				SELECT			reporting_date	AS 'Reporting Date'
							,	CASE	WHEN DATEPART(WEEKDAY, @Fecha) <  7 THEN
											DATEADD(d,-(1 + DATEPART(weekday,@Fecha)), @Fecha)
										WHEN DATEPART(WEEKDAY, @Fecha) >= 7 THEN
											DATEADD(d, -1 ,	@Fecha)
										END			AS		'Reporting Week'
							,	ord_maint_activity_type_key
							,	[count]
							,	CASE WHEN	mco LIKE ('%N/L%')	THEN 'NM N/L' ELSE CONCAT('NM',' ',mco) END AS 'MCO'
							,	CASE																	
								WHEN region in ('CN','EN')	THEN 'NL'
								WHEN region in ('CS','ES')	THEN 'SL'
								WHEN region =	'WE'		THEN 'TV'
								ELSE 'NA'
								END AS 'Region'
							,	age_total
			
							,	CASE WHEN	[ord_maint_activity_type_key] IN ('NM1','NM2','NM6') THEN 'NM CUSDR' ELSE 'NM Non-CUSDR' END AS 'CUSDR/Non-CUSDR'
			
							,	CASE  
									WHEN	[ord_maint_activity_type_key]	='NM1'	THEN	'NM1 (Customer)'					
									WHEN	[ord_maint_activity_type_key]	='NM2'	THEN	'NM2 (H&S Customer)'				
									WHEN	[ord_maint_activity_type_key]	='NM3'	THEN	'NM3 (H&S Non-Customer)'			
									WHEN	[ord_maint_activity_type_key]	='NM4'	THEN	'NM4 (Leakage Enabling)'			
									WHEN	[ord_maint_activity_type_key]	='NM5'	THEN	'NM5 (Network Maintenance)'		
									WHEN	[ord_maint_activity_type_key]	='NM6'	THEN	'NM6 - (Water Quality - Customer)'
									WHEN	[ord_maint_activity_type_key]	='NM7'	THEN	'NM7 - (Water Quality - Lead Pipe)'
									ELSE													'NM - (Other)'
								END AS 'NM Definition'

				FROM cbg_cdm_total_open_operations
				WHERE		[stk_category]	=	'Water Network R&M'
						AND	(mco				!=	'NA')-- OR mco IS NOT NULL)
						AND [ord_maint_activity_type_key] LIKE 'NM%'
						AND [opr_operation_number_work_centre_text] LIKE 'Water R&M%'
						)
						,
	BASETW	AS	(
				SELECT * FROM BASE
				WHERE [Reporting Date] = [Reporting Week]
				UNION ALL
				SELECT		[Reporting Date]
						,	[Reporting Week]
						,	ord_maint_activity_type_key
						,   [count]
						,	MCO
						,	'TW' AS Region
						,	age_total
						,	[CUSDR/Non-CUSDR]
						,	[NM Definition]
				FROM BASE
				WHERE [Reporting Date] = [Reporting Week] 
				)

SELECT		
			Region
		,	[NM Definition] as 'Metric'
		,	SUM([count]) AS 'Metric Value'
FROM		BASETW
GROUP BY	Region, ord_maint_activity_type_key, [NM Definition]

UNION ALL

SELECT		
			Region
		,	[CUSDR/Non-CUSDR] AS 'Metric'
		,	SUM([count]) AS 'Metric Value'
FROM		BASETW
GROUP BY	Region, [CUSDR/Non-CUSDR]

UNION ALL

SELECT		
			Region
		,	CONCAT([CUSDR/Non-CUSDR],' ','Age') AS 'Metric'
		,	CAST(SUM(age_total) AS FLOAT)/ CAST(SUM([count]) AS FLOAT) AS 'Metric Value'
FROM		BASETW
GROUP BY	Region, CONCAT([CUSDR/Non-CUSDR],' ','Age')

UNION ALL

SELECT		
			Region
		,	MCO AS 'Metric'
		,	SUM([count]) AS 'Metric Value'

FROM		BASETW
GROUP BY	Region, MCO
    ;''',engine)
QRY_OP_TOW_TRACK.to_csv (r'C:\CBG Friday am Pack\PySQL Outputs\Raw Files\Operations Outstanding Tracker query.csv', index = False)
now = datetime.datetime.now()
logging.info(f'{now} - Operations TOW Tracker Query Run and Stored in CSV File.')   
### OPERATIONS
QRY_OP = pd.read_sql_query('''
    DECLARE @Fecha DATE;
    SET @Fecha = CAST(GETDATE() AS DATE);
    WITH BASE AS (
                    SELECT		opr_operation_number_key						AS 'OPR_Operation Number - Key'
                                ,	CASE																		--4a Node
                                                                                        WHEN region in ('CN','EN')	THEN 'NL'
                                                                                        WHEN region in ('CS','ES')	THEN 'SL'
                                                                                        WHEN region =	'WE'		THEN 'TV'
                                                                                        ELSE 'NA'
                                        END AS	'Region'

                            ,	opr_operation_actual_end_date					AS 'OPR_Operation Actual End Date'
                            ,	flag_complete									AS 'Flag: Complete'

                            ,	DATEADD(DAY,15,opr_op_crtd_date) AS 'Target 15 Days'	
                            ,mco_aot
                            ,ord_maint_activity_type_key
                            ,opr_op_crtd_date

                    FROM	[dbo].[cbg_cdm_output_operations]
                    WHERE 
                            [opr_operation_number_work_centre_text] LIKE	('%Water R&M%')				--First Node
                    AND		opr_control_key_key						=		'PM03'						--Second Node
                    AND		[stk_category]							=		'Water Network R&M'			--3rd Node
                    AND		(mco									!=		'NA'						--3rd Node
                    OR		mco										IS NOT NULL)						--3rd Node
                    AND		aot_category							=		'Water Network R&M'			--3rd Node
                    AND		(mco_aot								!=		'NA'						--3rd Node
                    OR		mco_aot									IS NOT NULL)						--3rd Node
                    )
                    ,
        BASE1	AS	(
                    SELECT * FROM BASE
                    UNION ALL
                    SELECT		[OPR_Operation Number - Key]				AS 'OPR_Operation Number - Key'
                            ,	'TW'								AS 'Region'
                            ,	[OPR_Operation Actual End Date]				AS 'OPR_Operation Actual End Date'
                            ,	[Flag: Complete]							AS 'Flag: Complete'
                            ,	[Target 15 Days]
                            ,	mco_aot
                            ,	ord_maint_activity_type_key
                            ,	opr_op_crtd_date
                    FROM BASE
                    )
                    ,
        BASE2	AS	(
                    SELECT			* 
                                    ,	CASE	WHEN DATEPART(WEEKDAY, [Target 15 Days]) != 7 THEN
                                                DATEADD(d, 6 - DATEPART(weekday,[Target 15 Days]), [Target 15 Days])
                                            WHEN DATEPART(WEEKDAY, [Target 15 Days]) = 7 THEN
                                                DATEADD(d, 6 ,	[Target 15 Days])
                                            END			AS		'Week Ending'
                    FROM BASE1
                    WHERE	[Flag: Complete] = 1	
                    AND		[OPR_Operation Actual End Date] IS NOT NULL					
                    AND		mco_aot		= 'Mains'
                    AND		ord_maint_activity_type_key = 'AL'
                    )
                    ,
        BASE3	AS	(
                    SELECT			*
                                ,	'AL Mains Completed 15 Days' AS 'Metric'
                                ,	CASE	
                                            WHEN DATEDIFF(day, [Target 15 Days], [OPR_Operation Actual End Date]) > 0 THEN 0
                                            ELSE 1
                                            END AS 'Flag: Al Mains Comp < 15 Days'					
                    FROM BASE2
        
        
        
        
        
                    )
                    ,
        BASE4	AS	(
                    SELECT			Region
                                ,	Metric
                                --,	[Target 15 Days]
                                ,	AVG(CAST([Flag: Al Mains Comp < 15 Days] AS FLOAT)) AS 'Metric Value'
                                ,	[Week Ending]

                                    
                    FROM BASE3

                    --Latest Week
                    WHERE	DATEDIFF(DAY,[Week Ending],@Fecha) <=7
                    AND		DATEDIFF(DAY,[Week Ending],@Fecha) >=0 

                    GROUP BY Region, Metric, [Week Ending] --,[Target 15 Days]
                    )
                    
    SELECT 			Region
                ,	Metric
                ,	SUM([Metric Value]) AS 'Metric Value'
    FROM BASE4
    GROUP BY Region, Metric

    ;''',engine)
QRY_OP.to_csv(r'C:\CBG Friday am Pack\PySQL Outputs\Raw Files\Operations_Filtered.csv', index = False)
now = datetime.datetime.now()
logging.info(f'{now} - Operations Query Run and Stored in CSV File.')  
### CSL ACTIVITY OUTSTANDING TRACKER
QRY_CSL_ACT_TOW_TRACK = pd.read_sql_query('''
	DECLARE @Fecha DATE;
    SET @Fecha = CAST(GETDATE() AS DATE);
    WITH BASE AS	(
					SELECT		[reporting_date] AS	'Reporting Date'
								,	CASE	WHEN DATEPART(WEEKDAY, @Fecha) < 7 THEN
												DATEADD(d, -(1 + DATEPART(weekday,@Fecha)), @Fecha)
											WHEN DATEPART(WEEKDAY, @Fecha) >= 7 THEN
												DATEADD(d, -1,	@Fecha)
											END			AS		'Reporting Week'
								,	CASE	WHEN region in ('CN','EN')	THEN 'NL'
											WHEN region in ('CS','ES')	THEN 'SL'
											WHEN region =	'WE'		THEN 'TV'
											ELSE 'NA'
									END AS 'Region'
								,	CONCAT('CSL', ' ', work_type_initial) AS 'Metric'
								,	count_of_activities
								
					FROM		[dbo].[cbg_cdm_total_open_csl_activities]
					WHERE		[source]	!=	'Smart Metering'
							AND	work_flow_initial != 'Wastage'
							AND	work_type_initial	IN ('Unproven','Process','Fix')
							
					)
					,
  	BASETW	AS		(
					SELECT * FROM BASE
					WHERE [Reporting Date] = [Reporting Week]
					UNION ALL
					SELECT		[Reporting Date]
							,	[Reporting Week]
							,	'TW' AS Region
							,	Metric
							,	count_of_activities
					FROM BASE
					WHERE [Reporting Date] = [Reporting Week] 
					)
					

	SELECT		Region
			,	CASE WHEN Metric = 'CSL Fix' THEN 'CSL Repair' ELSE Metric END AS 'Metric'
			,	SUM(count_of_activities) AS 'Metric Value'
					
	FROM BASETW
	WHERE Region IS NOT NULL AND Region != 'NA'
	GROUP BY Region, Metric
	ORDER BY Region
    ;''',engine)
QRY_CSL_ACT_TOW_TRACK.to_csv (r'C:\CBG Friday am Pack\PySQL Outputs\Raw Files\CSL Activities Outstanding.csv', index = False)
now = datetime.datetime.now()
logging.info(f'{now} - CSL Activities TOW Tracker Query Run and Stored in CSV File.')  
###CONTACTS
QRY_CONTACTS = pd.read_sql_query('''
    DECLARE @Fecha DATE;
    SET @Fecha = CAST(GETDATE() AS DATE);
    WITH BASE AS	(
                    SELECT		opr_operation_number_key						AS 'OPR_Operation Number - Key'
                            ,	lead_order										AS 'Lead Order'
                            ,	CASE																		--4a Node
                                                        WHEN region in ('CN','EN')	THEN 'NL'
                                                        WHEN region in ('CS','ES')	THEN 'SL'
                                                        WHEN region =	'WE'		THEN 'TV'
                                                        ELSE 'NA' 
                                END AS 'Region'
                            ,	opr_operation_actual_end_date					AS 'OPR_Operation Actual End Date'
                            ,	ord_maint_activity_type_key						AS 'ORD_Maint. Activity Type - Key'
                            ,	mco_aot											AS 'MCO (AOT)'
                            ,	flag_tow										AS 'Flag: TOW'
                            ,	LEFT(opr_operation_number_key,8) AS 'Work Order'  --NODE 1 LINE 2-0 :Work Order
                        
                            --Week Ending Node #10
                            -----------------------
                            ,	CASE	WHEN DATEPART(WEEKDAY, opr_operation_actual_end_date) != 7 THEN
                                            DATEADD(d,6- DATEPART(weekday,opr_operation_actual_end_date), opr_operation_actual_end_date)
                                        WHEN DATEPART(WEEKDAY, opr_operation_actual_end_date) = 7 THEN
                                            DATEADD(d,-1 + DATEPART(weekday,opr_operation_actual_end_date),	opr_operation_actual_end_date)
                                        END			AS		'Week Ending vs Op End Date'

                            ,	DATEADD(DAY,15,opr_op_crtd_date) AS 'Target 15 Days'	--Target 15 Days Node Node 4V


                    FROM	[dbo].[cbg_cdm_output_operations] B
                    WHERE 
                            [opr_operation_number_work_centre_text] LIKE	('%Water R&M%')				--First Node
                    AND		opr_control_key_key						=		'PM03'						--Second Node
                    AND		[stk_category]							=		'Water Network R&M'			--3rd Node
                    AND		(mco										!=		'NA'						--3rd Node
                    OR		mco										IS NOT NULL)							--3rd Node
                    AND		aot_category							=		'Water Network R&M'			--3rd Node
                    AND		(mco_aot									!=		'NA'						--3rd Node
                    OR		mco_aot									IS NOT NULL)							--3rd Node
                    AND	NOT [flag_cancelled]						=		1							--Node 5 Not Cancelled
                    AND		mco_aot									IN		('Mains','Comms','Others')	--Node 6 Only MCO
                    AND	NOT	(flag_complete = 1	AND opr_operation_actual_end_date IS NULL)				--Node 7 Discard Comp with no date
                    AND NOT (flag_tow = 0 AND flag_complete = 0)										--Node 8 Only count Open or Complete (Discard)
                    AND		ord_maint_activity_type_key = 'VS'											--NODE 2 LINE 2-0 :VS Only
                    )
                    ,
    --ADD THAMES WATER
    BASETW AS	(
                SELECT * FROM BASE
                UNION ALL
                SELECT			[OPR_Operation Number - Key]
                            ,	[Lead Order]
                            ,	'TW' as 'Region'
                            ,	[OPR_Operation Actual End Date]
                            ,	[ORD_Maint. Activity Type - Key]
                            ,	[MCO (AOT)]
                            ,	[Flag: TOW]
                            ,	[Work Order] 
                            ,	[Week Ending vs Op End Date]
                            ,	[Target 15 Days]	
                FROM BASE
                )
                ,
    --OPERATIONS AND MERGE FROM CONTACTS
                    
    BASE2 AS	(
                    SELECT * FROM BASETW B
                    LEFT JOIN 	(
                                SELECT			work_order_number AS 'Work Order C'								--NODE 5 :Filter
                                            ,	MIN(crm_dhc_received_date) AS 'CRM_DHC Received Date_Min'		--NODE 2 (L 2 1) : Aggregate & NODE 5 : Filter (Renaming)
                                            ,	DATEADD(DAY,5,MIN(crm_dhc_received_date))	AS 'Target 5 Days'		--NODE 3 (L 2 1) : 'Target 5 Days'
                                            ,	DATEADD(DAY,9,MIN(crm_dhc_received_date))	AS 'Target 9 Days'		--NODE 4 (L 2 1) : 'Target 9 Days'
                                FROM [dbo].[cbg_cdm_output_contacts] 
                                GROUP BY work_order_number
                                ) A

                    ON	A.[Work Order C] = B.[Work Order]
                )
                ,

    BASE3 AS	(
    --'VS Completed in 9 Days'
                SELECT			'VS Completed in 9 Days' AS 'Metric'
                            ,	[CRM_DHC Received Date_Min]
                            ,	[Target 9 Days] as 'Target'  --Filter Node (Renaming) 
                            ,	[Lead Order]
                            ,	Region
                            ,	MAX([OPR_Operation Actual End Date]) AS 'OPR_Operation Actual End Date_Max'
                            ,	SUM([Flag: TOW])		AS 'Flag: TOW_Sum'
                            -- NODE Flag: 9 Day Compliance
                            ,	CASE	WHEN SUM([Flag: TOW]) > 0 THEN 0
                                        WHEN DATEDIFF(DAY, [Target 9 Days], MAX([OPR_Operation Actual End Date])) > 0 THEN 0
                                        ELSE 1
                            END AS 'Flag: Compliance'
                            ,	CASE	WHEN DATEPART(WEEKDAY, [Target 9 Days]) != 7 THEN
                                            DATEADD(d,6- DATEPART(weekday,[Target 9 Days]), [Target 9 Days])
                                        WHEN DATEPART(WEEKDAY, [Target 9 Days]) = 7 THEN
                                            DATEADD(d,6 ,	[Target 9 Days])
                                END			AS		'Week Ending'
                FROM BASE2
                GROUP BY [Lead Order], [Target 9 Days],Region,[CRM_DHC Received Date_Min]

                UNION

                --'VS Completed in 5 Days'
                SELECT			'VS Completed in 5 Days' AS 'Metric'
                            ,	[CRM_DHC Received Date_Min]
                            ,	[Target 5 Days] as 'Target'  --Filter Node (Renaming) 
                            ,	[Lead Order]
                            ,	Region
                            ,	MAX([OPR_Operation Actual End Date]) AS 'OPR_Operation Actual End Date_Max'
                            ,	SUM([Flag: TOW])		AS 'Flag: TOW_Sum'
                            -- NODE Flag: 5 Day Compliance
                            ,	CASE	WHEN SUM([Flag: TOW]) > 0 THEN 0
                                        WHEN DATEDIFF(DAY, [Target 5 Days], MAX([OPR_Operation Actual End Date])) > 0 THEN 0
                                        ELSE 1
                            END AS 'Flag: Compliance'
                            ,	CASE	WHEN DATEPART(WEEKDAY, [Target 5 Days]) != 7 THEN
                                            DATEADD(d,6- DATEPART(weekday,[Target 5 Days]), [Target 5 Days])
                                        WHEN DATEPART(WEEKDAY, [Target 5 Days]) = 7 THEN
                                            DATEADD(d,6 ,	[Target 5 Days])
                                END			AS		'Week Ending'
                FROM BASE2
                GROUP BY [Lead Order], [Target 5 Days],Region,[CRM_DHC Received Date_Min]

                UNION

                --VS Mains Completed in 5 Days
                SELECT			'VS Mains Completed in 5 Days' AS 'Metric'
                            ,	[CRM_DHC Received Date_Min]
                            ,	[Target 5 Days] as 'Target'  --Filter Node (Renaming) 
                            ,	[Lead Order]
                            ,	Region
                            ,	MAX([OPR_Operation Actual End Date]) AS 'OPR_Operation Actual End Date_Max'
                            ,	SUM([Flag: TOW])		AS 'Flag: TOW_Sum'
                            -- NODE Flag: 5 Day Compliance
                            ,	CASE	WHEN SUM([Flag: TOW]) > 0 THEN 0
                                        WHEN DATEDIFF(DAY, [Target 5 Days], MAX([OPR_Operation Actual End Date])) > 0 THEN 0
                                        ELSE 1
                            END AS 'Flag: Compliance'
                            ,	CASE	WHEN DATEPART(WEEKDAY, [Target 5 Days]) != 7 THEN
                                            DATEADD(d,6- DATEPART(weekday,[Target 5 Days]), [Target 5 Days])
                                        WHEN DATEPART(WEEKDAY, [Target 5 Days]) = 7 THEN
                                            DATEADD(d,6 ,	[Target 5 Days])
                                END			AS		'Week Ending'

                FROM BASE2
                WHERE [MCO (AOT)] = 'Mains'
                GROUP BY [Lead Order], [Target 5 Days],Region,[CRM_DHC Received Date_Min]
                )

    SELECT			Region
                ,	Metric
                --,	[Week Ending]
                ,	AVG(CAST([Flag: Compliance] AS FLOAT)) AS 'Metric Value'
    FROM BASE3	
    WHERE			DATEDIFF(DAY,[Week Ending],@Fecha) <=7
            AND		DATEDIFF(DAY,[Week Ending],@Fecha) >=0 
    GROUP BY Region, Metric, [Week Ending]
    order by Region
    ;''',engine)
QRY_CONTACTS.to_csv (r'C:\CBG Friday am Pack\PySQL Outputs\Raw Files\Contacts_Filtered.csv', index = False)
now = datetime.datetime.now()
logging.info(f'{now} - Contacts Query Run and Stored in CSV File.')  


##################
#AFTER SQL QUERIES
##################

##Files
OPERATIONS  = pd.read_csv(r'C:\CBG Friday am Pack\PySQL Outputs\Raw Files\Operations_Filtered.csv')
CONTACTS    = pd.read_csv(r'C:\CBG Friday am Pack\PySQL Outputs\Raw Files\Contacts_Filtered.csv')
OP_TRACKER  = pd.read_csv(r'C:\CBG Friday am Pack\PySQL Outputs\Raw Files\Operations Outstanding Tracker query.csv')
CSL_ACT_TAB = pd.read_csv(r'C:\CBG Friday am Pack\PySQL Outputs\Raw Files\CSL Activities Table.csv') 
CSL_ACT_TOW = pd.read_csv(r'C:\CBG Friday am Pack\PySQL Outputs\Raw Files\CSL Activities Outstanding.csv')   
logging.info(f'{now} : CSV Files Loaded, starting final data transformations...')

##TRANSFORMATIONS
now = datetime.datetime.now()
if OPERATIONS.shape[0] !=0:
    OPERATIONS = OPERATIONS.pivot_table(values='Metric Value', index = 'Metric', columns = 'Region')
else:
    logging.error('Operations Table not Populated.')

if CONTACTS.shape[0] != 0:
    CONTACTS = CONTACTS.pivot_table(values='Metric Value', index = 'Metric', columns = 'Region')
else:
    logging.error('Contacts Table not Populated.')

if OP_TRACKER.shape[0] != 0:
   OP_TRACKER = OP_TRACKER.pivot_table(values='Metric Value', index = 'Metric', columns = 'Region')
   OP_TRACKER = OP_TRACKER.reindex(['NM - (Other)', 'NM1 (Customer)', 'NM2 (H&S Customer)', 'NM3 (H&S Non-Customer)','NM4 (Leakage Enabling)', 'NM5 (Network Maintenance)','NM6 - (Water Quality - Customer)',
       'NM7 - (Water Quality - Lead Pipe)', 'NM Non-CUSDR', 'NM CUSDR', 'NM Mains',  'NM Comms', 'NM Others', 'NM N/L', 'NM Non-CUSDR Age', 'NM CUSDR Age']      )
else:
    logging.error('Operations Tracker Table not Populated.')

if CSL_ACT_TAB.shape[0] != 0:
    CSL_ACT_TAB = CSL_ACT_TAB.pivot_table(values='Metric Value', index = 'Metric', columns = 'Region')
else:
    logging.error('CSL Activities Table not Populated.')

if CSL_ACT_TOW.shape[0] != 0:
    CSL_ACT_TOW = CSL_ACT_TOW.pivot_table(values='Metric Value', index = 'Metric', columns = 'Region')
    CSL_ACT_TOW = CSL_ACT_TOW.reindex(['CSL Unproven','CSL Process', 'CSL Repair'])
else:
   logging.error('CSL Activities Oustanding Table (tracker) not Populated.')


def concat(*args):
    return pd.concat([x for x in args if not x.empty])
TOW = concat(*[OP_TRACKER,OPERATIONS,CONTACTS,CSL_ACT_TOW,CSL_ACT_TAB])
TOW = TOW[['NL',	'SL',	'TV','TW']]
TOW.to_csv(r'C:\CBG Friday am Pack\PySQL Outputs\Report\CBG Friday Am Pack TOW.csv')
TOW.to_excel(r'C:\CBG Friday am Pack\PySQL Outputs\Report\CBG Friday Am Pack TOW.xlsx')
now = datetime.datetime.now()
logging.info(f'{now} : Friday AM Pack Tow Report File Created.')

##########################
#Copy Files to Sharepoint#
##########################
now = datetime.datetime.now()
logging.info(f'{now} : Copying Files into Sharepoint Site. Thames Water Utilities Limited\Operations Data & Insight Team - NM Figures\Test.')
Output_Location = 'C:/CBG Friday am Pack/PySQL Outputs/Report/'
subprocess.call(['robocopy', Output_Location,f'C:/Users/{user}/Thames Water Utilities Limited/Operations Data & Insight Team - NM Figures','CBG Friday Am Pack TOW.csv', r"/S"])
subprocess.call(['robocopy', Output_Location,f'C:/Users/{user}/Thames Water Utilities Limited/Operations Data & Insight Team - NM Figures','CBG Friday Am Pack TOW.xlsx', r"/S"])
subprocess.call(['robocopy', Output_Location,f'C:/Users/{user}/Thames Water Utilities Limited/Operations Data & Insight Team - NM Figures','CBG Friday Am Pack Fix.csv', r"/S"])

now = datetime.datetime.now()
logging.info(f'{now} :"Friday Am Pack Tow and Fix now Uploaded to SharePoint, process finished')
print(f'{now} :"Friday Am Pack Tow and Fix now Uploaded to SharePoint, process finished')
