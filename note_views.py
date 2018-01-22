%python

import subprocess
import pandas as pd
import dateutil


# Get rows from logs

def run_cmd(cmd):
    subprPopen = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    cstdout, cstderr = subprPopen.communicate()
    return str(cstdout.decode('utf-8'))
    
command = 'echo $ZEPPELIN_HOME'
logDir = run_cmd(command)[:-1] + '/logs/'

command = 'grep GET_NOTE {logDir}zeppelin-zeppelin-*'.format(logDir=logDir)
get_note_list = run_cmd(command).split('\n')


# Process logs to DataFrame

data = []
for s in get_note_list:
    try:
        date = s.split('INFO [')[1].split()[0]
        user = s.split(' : GET_NOTE : ')[0].split(': ')[-1]
        note_id = s.split(' : GET_NOTE : ')[1]
    except IndexError:
        pass
    data.append([date, user, note_id])
    
df = pd.DataFrame.from_records(data, columns=['date', 'user_nm', 'note_id'])


# Add dates

df['date'] = df['date'].apply(dateutil.parser.parse, dayfirst=False)
df['week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)
df['month'] = df['date'].dt.to_period('M').apply(lambda r: r.start_time)
df = df[df['date'] >= '2017-11-27']


# Aggregate

day_stats = pd.DataFrame()
week_stats = pd.DataFrame()

day_stats['views'] = df.groupby('date')['note_id'].count()
day_stats['users'] = df.groupby('date')['user_nm'].nunique()
day_stats['notes'] = df.groupby('date')['note_id'].nunique()
week_stats['users'] = df.groupby('week')['user_nm'].nunique()
week_stats['notes'] = df.groupby('week')['note_id'].nunique()


# Display

print('%html <b>Unique users and unique notes per day</b>')
print('%table ' + day_stats.to_csv(sep='\t', index=True))
print('%html <b>Note views per day<b>')
print('%table ' + day_stats.to_csv(sep='\t', index=True))
print('%html <b>Unique users and unique notes per week<b>')
print('%table ' + week_stats.to_csv(sep='\t', index=True))