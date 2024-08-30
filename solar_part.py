{\rtf1\ansi\ansicpg1252\cocoartf2636
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 ArialMT;}
{\colortbl;\red255\green255\blue255;\red26\green26\blue26;\red255\green255\blue255;}
{\*\expandedcolortbl;;\cssrgb\c13333\c13333\c13333;\cssrgb\c100000\c100000\c100000;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs26 \cf2 \cb3 \expnd0\expndtw0\kerning0
from sqlalchemy import create_engine\cb1 \
\cb3 import numpy as np\cb1 \
\cb3 import pandas as pd\cb1 \
\cb3 import seaborn as sns\cb1 \
\cb3 from sklearn import linear_model\cb1 \
\cb3 \'a0\cb1 \
\cb3 \'a0\cb1 \
\cb3 # import "static" initial metrics at time of participation, apply the acquisition date, and impute fico buckets\cb1 \
\cb3 \'a0\cb1 \
\cb3 Server = 'fcu-az-edwprep1'\cb1 \
\cb3 Database = 'GrowAnalyticsDb'\cb1 \
\cb3 Driver = 'ODBC Driver 17 for SQL Server'\cb1 \
\cb3 Database_con = f'mssql://@\{Server\}/\{Database\}?driver=\{Driver\}'\'a0\'a0\'a0\cb1 \
\cb3 \'a0\cb1 \
\cb3 static = pd.read_sql_query('''\cb1 \
\cb3 \'a0\'a0 SELECT\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0 [LoanNumber]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[AsOfDate]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[OriginalLoanAmount] * 0.90 as [OriginalLoanAmount]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[CurrentBalance] * 0.90 as [CurrentBalance]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[OriginalTerm]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[FICOScore]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[DateOfLoan]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[OriginalRate]\cb1 \
\cb3 \'a0 FROM [dbo].[SolarAcquisition]\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0'''\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 , create_engine(Database_con).connect())\cb1 \
\cb3 \'a0\cb1 \
\cb3 static.AsOfDate # not date\cb1 \
\cb3 \'a0\cb1 \
\cb3 static.AsOfDate = pd.to_datetime(static.AsOfDate)\cb1 \
\cb3 static.DateOfLoan = pd.to_datetime(static.DateOfLoan)\cb1 \
\cb3 \'a0\cb1 \
\cb3 static['AcqDate'] = pd.to_datetime('2022-11-29')\cb1 \
\cb3 \'a0\cb1 \
\cb3 static['AcqDateF'] = static.AcqDate.dt.to_period('M').dt.to_timestamp() + pd.DateOffset(months = 1)\cb1 \
\cb3 \'a0\cb1 \
\cb3 static['DateOfLoanF'] = static.DateOfLoan.dt.to_period('M').dt.to_timestamp() + pd.DateOffset(months = 1)\cb1 \
\cb3 \'a0\cb1 \
\cb3 static = static.assign(\cb1 \
\cb3 \'a0\'a0\'a0 MoB =\cb1 \
\cb3 \'a0\'a0\'a0 ((static.AcqDateF.dt.year - static.DateOfLoanF.dt.year) * 12) +\cb1 \
\cb3 \'a0\'a0\'a0 (static.AcqDateF.dt.month - static.DateOfLoanF.dt.month)\cb1 \
\cb3 )\cb1 \
\cb3 \'a0\cb1 \
\cb3 conditions = [\cb1 \
\cb3 \'a0\'a0\'a0 (static['FICOScore'].lt(620)),\cb1 \
\cb3 \'a0\'a0\'a0 (static['FICOScore'].ge(620) & static['FICOScore'].lt(640)),\cb1 \
\cb3 \'a0\'a0\'a0 (static['FICOScore'].ge(640) & static['FICOScore'].lt(680)),\cb1 \
\cb3 \'a0\'a0\'a0 (static['FICOScore'].ge(680) & static['FICOScore'].lt(700)),\cb1 \
\cb3 \'a0\'a0\'a0 (static['FICOScore'].ge(700) & static['FICOScore'].lt(740)),\cb1 \
\cb3 \'a0\'a0\'a0 (static['FICOScore'].ge(740)),\cb1 \
\cb3 \'a0\'a0\'a0 ]\cb1 \
\cb3 \'a0\cb1 \
\cb3 choices = ['Sub Prime', 'Near Prime 620 - 639', 'Near Prime 640 - 679', 'Prime 680 - 699', 'Prime 700 - 739', 'Super Prime']\cb1 \
\cb3 \'a0\cb1 \
\cb3 static['fico_bucket'] = np.select(conditions, choices)\cb1 \
\cb3 \'a0\cb1 \
\cb3 static.LoanNumber = static['LoanNumber'].str.slice_replace(6,9, '')\cb1 \
\cb3 \'a0\cb1 \
\cb3 \'a0\cb1 \
\cb3 # calculate mins, max, avgs, etc.of various metrics\cb1 \
\cb3 \'a0\cb1 \
\cb3 def static_func():\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0count = static.LoanNumber.nunique()\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0overall = pd.DataFrame(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{'MinDate': [min(static.DateOfLoan)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'MaxDate': [max(static.DateOfLoan)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'OrigBal': [sum(static.OriginalLoanAmount)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'PresBal': [sum(static.CurrentBalance)]\}\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0averages = pd.DataFrame(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{'MoB': [(static.MoB).mean()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'Term': [(static.OriginalTerm / 12).mean()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'OrigFICO': [(static.FICOScore).mean()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'IntRate': [(static.OriginalRate).mean()]\}\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0weightedaverages = pd.DataFrame(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{'MoB': [np.average(static.MoB, weights = static.OriginalLoanAmount)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'Term': [np.average(static.OriginalTerm / 12, weights = static.OriginalLoanAmount)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'OrigFICO': [np.average(static.FICOScore, weights = static.OriginalLoanAmount)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'IntRate': [np.average(static.OriginalRate, weights = static.OriginalLoanAmount)]\}\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0mins = pd.DataFrame(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{'MoB': [(static.MoB).min()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'Term': [(static.OriginalTerm / 12).min()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'OrigFICO': [(static.FICOScore).min()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'IntRate': [(static.OriginalRate).min()]\}\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0maxs = pd.DataFrame(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{'MoB': [(static.MoB).max()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'Term': [(static.OriginalTerm / 12).max()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'OrigFICO': [(static.FICOScore).max()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'IntRate': [(static.OriginalRate).max()]\}\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0cp = pd.concat([\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 averages,\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 weightedaverages,\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 mins,\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 maxs\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 ])\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0return [count, overall, cp]\cb1 \
\cb3 \'a0\cb1 \
\cb3 # This output is in the Performance at Acquisition area of the Summary Statistics tab of deliverables/Participation analysis as of MM YYYY. As it is at acquisition it does not require an update.\cb1 \
\cb3 \'a0\cb1 \
\cb3 static_func()[0]\cb1 \
\cb3 static_func()[1]\cb1 \
\cb3 static_func()[2]\cb1 \
\cb3 \'a0\cb1 \
\cb3 # import monthly performance data and calculate MoP, MoB, expected princ, expected and actual payments, and monthly CPR\cb1 \
\cb3 \'a0\cb1 \
\cb3 current = pd.read_sql_query('''\cb1 \
\cb3 \'a0\'a0 SELECT\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0[ReportDate]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[LoanID]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[OriginationDate]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[MaturityDate]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[OriginalLoanBalance] * 0.90 as [OriginalLoanBalance]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[CurrentLoanBalance]\'a0 * 0.90 as [CurrentLoanBalance]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[ChargeOffDate]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[TotalChargeOffAmount]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 ,[InterestRate]\cb1 \
\cb3 \'a0 FROM [dbo].[SolarPerformance]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 '''\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 , create_engine(Database_con).connect())\cb1 \
\cb3 \'a0\cb1 \
\cb3 current = current.dropna(subset = ['LoanID'])\cb1 \
\cb3 \'a0\cb1 \
\cb3 current = current.drop_duplicates()\cb1 \
\cb3 \'a0\cb1 \
\cb3 current = current.merge(static[['LoanNumber', 'FICOScore', 'fico_bucket', 'OriginalTerm']], left_on = 'LoanID', right_on = 'LoanNumber', how = 'left')\cb1 \
\cb3 \'a0\cb1 \
\cb3 current['AsOfDate']= pd.to_datetime(current.ReportDate)\cb1 \
\cb3 \'a0\cb1 \
\cb3 current.OriginationDate = pd.to_datetime(current.OriginationDate)\cb1 \
\cb3 \'a0\cb1 \
\cb3 current['AcqDate'] = pd.to_datetime('2022-11-29')\cb1 \
\cb3 \'a0\cb1 \
\cb3 current['AcqDateF'] = current.AcqDate.dt.to_period('M').dt.to_timestamp() + pd.DateOffset(months = 1)\cb1 \
\cb3 \'a0\cb1 \
\cb3 current['OriginationDateF'] = current.OriginationDate.dt.to_period('M').dt.to_timestamp() + pd.DateOffset(months = 1)\cb1 \
\cb3 \'a0\cb1 \
\cb3 current['MoB'] = ((current['AsOfDate'].dt.year - current['OriginationDateF'].dt.year) * 12) + (current['AsOfDate'].dt.month - current['OriginationDateF'].dt.month)\cb1 \
\cb3 \'a0\cb1 \
\cb3 current['MoP'] = ((current['AsOfDate'].dt.year - current['AcqDateF'].dt.year) * 12) + (current['AsOfDate'].dt.month - current['AcqDateF'].dt.month)\cb1 \
\cb3 \'a0\cb1 \
\cb3 current['ExpPrinc'] = ((current.OriginalLoanBalance * (current.InterestRate/100/12)/(1 - (1 + current.OriginalLoanBalance) ** -(current.OriginalTerm))) + (1 + current.OriginalLoanBalance) ** (current.MoB) * (current.OriginalLoanBalance* (current.InterestRate/100/12) - (current.OriginalLoanBalance* (current.InterestRate/100/12)/(1 - (1 + current.OriginalLoanBalance) ** -(current.OriginalTerm)))))/(current.InterestRate/100/12)\cb1 \
\cb3 \'a0\cb1 \
\cb3 current = current.sort_values(['LoanNumber', 'MoB'], ascending=[True, True])\cb1 \
\cb3 \'a0\cb1 \
\cb3 # filter on latest and get mins, maxs, avgs, etc.\cb1 \
\cb3 \'a0\cb1 \
\cb3 current2 = current.loc[current['ReportDate'] == current['ReportDate'].max()]\cb1 \
\cb3 \'a0\cb1 \
\cb3 bal_at_part = current.loc[current['ReportDate'] == current['ReportDate'].min()]\cb1 \
\cb3 \'a0\cb1 \
\cb3 bal_at_part = bal_at_part.CurrentLoanBalance.sum()\cb1 \
\cb3 \'a0\cb1 \
\cb3 def current_func():\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0current_def = current2.loc[current2['CurrentLoanBalance'] > 0]\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0count = current_def.LoanNumber.nunique()\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0co_count = current_def.ChargeOffDate.count()\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0overall = pd.DataFrame(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{'MinDate': [min(current_def.OriginationDate)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'MaxDate': [max(current_def.OriginationDate)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'PresBal': [sum(current_def.CurrentLoanBalance)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'COAmount': [sum(current_def.TotalChargeOffAmount)]\}\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0averages = pd.DataFrame(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{'MoB': [(current_def.MoB).mean()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'Term': [(current_def.OriginalTerm / 12).mean()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'OrigFICO': [(current_def.FICOScore).mean()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'IntRate': [(current_def.InterestRate).mean()]\}\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0weightedaverages = pd.DataFrame(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{'MoB': [np.average(current_def.MoB, weights = current_def.OriginalLoanBalance)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'Term': [np.average(current_def.OriginalTerm / 12, weights = current_def.OriginalLoanBalance)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'OrigFICO': [np.average(current_def.FICOScore, weights = current_def.OriginalLoanBalance)],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'IntRate': [np.average(current_def.InterestRate, weights = current_def.OriginalLoanBalance)]\}\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0mins = pd.DataFrame(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{'MoB': [(current_def.MoB).min()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'Term': [(current_def.OriginalTerm / 12).min()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'OrigFICO': [(current_def.FICOScore).min()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'IntRate': [(current_def.InterestRate).min()]\}\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0maxs = pd.DataFrame(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 \{'MoB': [(current_def.MoB).max()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'Term': [(current_def.OriginalTerm / 12).max()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'OrigFICO': [(current_def.FICOScore).max()],\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 'IntRate': [(current_def.InterestRate).max()]\}\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0cp = pd.concat([\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 averages,\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 weightedaverages,\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 mins,\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 maxs\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 ])\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 \'a0\'a0\'a0\'a0return [count, co_count, overall, cp]\cb1 \
\cb3 \'a0\cb1 \
\cb3 # This output is in the Performance as of MM/DD/YYYY area of the Summary Statistics tab of deliverables/Participation analysis as of MM YYYY. Remaining loans , min/max date, and pres bal all should be updated. The table of avg, weighted avg, min, max can be copied and pasted from the `c&p` object of the output list.\cb1 \
\cb3 \'a0\cb1 \
\cb3 current_func()[0]\cb1 \
\cb3 current_func()[1]\cb1 \
\cb3 current_func()[2]\cb1 \
\cb3 current_func()[3]\cb1 \
\cb3 \'a0\cb1 \
\cb3 # breakdown by FICO and term for static vs most recent, OriginalTerm, beg count, present count, original balance, participation balance, present balance. Write to csv. This provides the update for the "paydowns" tab.\cb1 \
\cb3 \'a0\cb1 \
\cb3 (pd.merge(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0 (static.groupby(['fico_bucket', 'OriginalTerm']).size().reset_index(name = 'beg')\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 .merge(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 (current2.loc[current2['CurrentLoanBalance'] > 0]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .groupby(['fico_bucket', 'OriginalTerm'])\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .size()\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .reset_index(name = 'now')), how = 'left', on = ['fico_bucket', 'OriginalTerm']\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 ),\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 (static.groupby(['fico_bucket', 'OriginalTerm'], as_index = False)['OriginalLoanAmount'].sum()\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .merge(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 (\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 current.loc[current['ReportDate'] == current['ReportDate'].min()]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .groupby(['fico_bucket', 'OriginalTerm'], as_index = False).agg(part_bal = ('CurrentLoanBalance', 'sum'))\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 ), how = 'left', on = ['fico_bucket', 'OriginalTerm']\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 ), how = 'left', on = ['fico_bucket', 'OriginalTerm'])\cb1 \
\cb3 \'a0\'a0\'a0 .merge(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 (current2.loc[current2['CurrentLoanBalance'] > 0]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .groupby(['fico_bucket', 'OriginalTerm'])\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .agg(pres_bal = ('CurrentLoanBalance', 'sum'),\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 co_amount = ('TotalChargeOffAmount', 'sum'))\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 ), how = 'left', on = ['fico_bucket', 'OriginalTerm']\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0 .merge(\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 (current2.loc[current2['TotalChargeOffAmount'] > 0]\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .groupby(['fico_bucket', 'OriginalTerm'])\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .agg(co_count = ('TotalChargeOffAmount', 'count'))\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 ), how = 'left', on = ['fico_bucket', 'OriginalTerm']\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\'a0\'a0 .fillna('0')\cb1 \
\cb3 \'a0\'a0\'a0 .to_csv('solar.csv', index = False)\cb1 \
\cb3 \'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\cb1 \
\cb3 \'a0\cb1 \
\cb3 # pay down speed\cb1 \
\cb3 \'a0\cb1 \
\cb3 # total beginning balance\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_part = static.CurrentBalance.sum()\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_part = pd.DataFrame(\cb1 \
\cb3 \'a0\'a0\'a0\'a0 \{'pool': 1,\cb1 \
\cb3 \'a0\'a0\'a0\'a0 'orig': [(static.CurrentBalance).sum()]\}\cb1 \
\cb3 \'a0\'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\cb1 \
\cb3 # principal and exp remaining princ by MoP\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_aod = (current\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .groupby(['MoP'], as_index = False)\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .agg(prin = ('CurrentLoanBalance', 'sum'),\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 CUMPRINC = ('ExpPrinc', 'sum')))\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_aod["pool"] = 1\cb1 \
\cb3 \'a0\cb1 \
\cb3 # generate df for plotting\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_p = (\cb1 \
\cb3 \'a0\'a0\'a0 solar_aod\cb1 \
\cb3 \'a0\'a0\'a0 .merge(solar_part, on = ['pool'], how = 'left')\cb1 \
\cb3 \'a0\'a0\'a0 .eval('''\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 remn = prin / orig * 100\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 CUMPRINC_remn = CUMPRINC / orig * 100\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 ''')\cb1 \
\cb3 \'a0\'a0\'a0 )\cb1 \
\cb3 \'a0\cb1 \
\cb3 # then plot\cb1 \
\cb3 \'a0\cb1 \
\cb3 sns.lineplot(x='MoP', y='value', hue='variable',\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0data=pd.melt((solar_p\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .drop(columns = ['pool',\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0'orig',\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 'prin',\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 'CUMPRINC'])), ['MoP']))\cb1 \
\cb3 \'a0\cb1 \
\cb3 # plot makes no sense, above 100%\cb1 \
\cb3 \'a0\cb1 \
\cb3 # data exploration, amortized balance by loan through time\cb1 \
\cb3 \'a0\cb1 \
\cb3 cumprinc_by_loan = current[['AsOfDate', 'LoanID', 'ExpPrinc']].pivot(index = 'LoanID', columns = 'AsOfDate', values = 'ExpPrinc').fillna(0).reset_index()\cb1 \
\cb3 \'a0\cb1 \
\cb3 # data exploration, actual balance by loan through time\cb1 \
\cb3 \'a0\cb1 \
\cb3 princ_by_loan = current[['AsOfDate', 'LoanID', 'CurrentLoanBalance']].pivot(index = 'LoanID', columns = 'AsOfDate', values = 'CurrentLoanBalance').fillna(0).reset_index()\cb1 \
\cb3 \'a0\cb1 \
\cb3 # There are gaps, replace missing values with 0 so percentages get calculated properly\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar3 = princ_by_loan.melt(id_vars = ['LoanID'], var_name = 'AsOfDate', value_name = 'Principal')\cb1 \
\cb3 \'a0\cb1 \
\cb3 # calculate cpr from expected cpr (10% in this case)\cb1 \
\cb3 \'a0\cb1 \
\cb3 cpr_rate = 1 - (0.15 / 12)\cb1 \
\cb3 \'a0\cb1 \
\cb3 # new df for actual princ, exp princ, and cpr princ\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_exp_princ = (static[['LoanNumber', 'OriginalLoanAmount', 'CurrentBalance', 'OriginalRate', 'OriginalTerm', 'AcqDateF', 'DateOfLoanF']].drop_duplicates()\cb1 \
\cb3 .merge(solar3, how = 'left', left_on = 'LoanNumber', right_on = 'LoanID')\cb1 \
\cb3 .assign(MoB = lambda df: ((df['AsOfDate'].dt.year - df['DateOfLoanF'].dt.year) * 12) + (df['AsOfDate'].dt.month - df['DateOfLoanF'].dt.month),\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 MoP = lambda df: ((df['AsOfDate'].dt.year - df['AcqDateF'].dt.year) * 12) + (df['AsOfDate'].dt.month - df['AcqDateF'].dt.month),\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 exp_princ = lambda df: (((df.OriginalRate / 100 / 12) * df.OriginalLoanAmount/(1 - (1 + (df.OriginalRate / 100 / 12)) ** -df.OriginalTerm)) + (1 + (df.OriginalRate / 100 / 12)) ** df.MoB * ((df.OriginalRate / 100 / 12) * df.OriginalLoanAmount - ((df.OriginalRate / 100 / 12) * df.OriginalLoanAmount/(1 - (1 + (df.OriginalRate / 100 / 12)) ** -df.OriginalTerm))))/(df.OriginalRate / 100 / 12),\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 CPR = lambda df: df.exp_princ * (cpr_rate ** df.MoP))\cb1 \
\cb3 )\cb1 \
\cb3 \'a0\cb1 \
\cb3 # principal and exp remaining princ by MoP\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_aod = (solar_exp_princ\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .groupby(['MoP'], as_index = False)\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .agg(prin = ('Principal', 'sum'),\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 CUMPRINC = ('exp_princ', 'sum'),\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 cpr = ('CPR', 'sum')))\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_aod['orig'] = solar_part.orig[0]\cb1 \
\cb3 \'a0\cb1 \
\cb3 # new plotting df\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_p = (solar_aod\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 .eval('''\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 Remaining_Balance = prin / orig * 100\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 Amortized_Balance = CUMPRINC / orig * 100\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 Expected_Balance = cpr / orig * 100\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 prin_diff = prin - CUMPRINC\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 CPR = 1 - (prin / CUMPRINC) ** (12 / MoP)\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 smm = 1 - ((1 - CPR) ** (1 / 12))\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0 '''))\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\cb1 \
\cb3 # copy graph into CPR tab\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\cb1 \
\cb3 sns.lineplot(x='MoP', y='value', hue='variable',\cb1 \
\cb3 \'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0\'a0data=pd.melt((solar_p[['MoP', 'Remaining_Balance', 'Amortized_Balance', 'Expected_Balance']]), ['MoP']))\cb1 \
\cb3 \'a0\cb1 \
\cb3 # subset of columns for expected payoff model\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_cpr = solar_p[['MoP', 'prin', 'CUMPRINC', 'Remaining_Balance', 'CPR', 'smm']]\cb1 \
\cb3 \'a0\cb1 \
\cb3 # What is avg cpr?\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_cpr.CPR.drop(index = 0).mean() * 100\cb1 \
\cb3 \'a0\'a0\'a0\cb1 \
\cb3 # isolate most recent CPR and MoP, add to CPR and MoP fields.\cb1 \
\cb3 \'a0\cb1 \
\cb3 solar_p.loc[solar_p['MoP'] == solar_p.MoP.max()][['CPR', 'MoP']]\cb1 \
\cb3 \'a0\cb1 \
\cb3 # lm of MoP as a function of CPR * remn bal. Used to predict MoP when balance = 0\cb1 \
\cb3 # lm was chosen because it was found to be the only model that would hit 0, even though in reality it would never cross over. Other models like logarithmic regression would skirt along but never reach 0, and a "assumed zero" would need to be arbitrarily chosen.\cb1 \
\cb3 \'a0\cb1 \
\cb3 X = solar_p[['CPR', 'Remaining_Balance']]\cb1 \
\cb3 y = solar_p[['MoP']]\cb1 \
\cb3 \'a0\cb1 \
\cb3 regr = linear_model.LinearRegression()\cb1 \
\cb3 regr.fit(X, y)\cb1 \
\cb3 \'a0\cb1 \
\cb3 # when will remn bal hit 0? CPR input is mean of cpr through time for portfolio . Add to CPR tab of deliverables/participation analysis in Predicted 0 Balance MoP. Extreme CPR values cause results that make no sense, but small changes only add or subtract a few months for expected 0.\cb1 \
\cb3 \'a0\cb1 \
\cb3 regr.predict([[solar_cpr.CPR.drop(index = 0).mean(), 0]])}