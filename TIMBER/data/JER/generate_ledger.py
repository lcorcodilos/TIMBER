import glob, pandas

_columns = ['tag','ver','year','ULflag','dataOrMC','filename']

df = pandas.DataFrame(columns=_columns)

for filename in glob.glob('*.tar.gz'):
    pieces = filename.split('.')[0].split('_')

    if len(pieces) > 3:
        raise IndexError('Expected 2 underscores ("_") in tarball names but found something different (%s). Algorithm assumes 2 underscores.'%filename)

    APVflag = True if 'APV' in pieces[0] else False

    d_row = {c:None for c in _columns}

    d_row['tag']      = pieces[0]
    d_row['ver']      = pieces[1]
    d_row['ULflag']   = True if 'UL' in d_row['tag'] else False
    d_row['year']     = '20' + (d_row['tag'][-5:] if APVflag else d_row['tag'][-2:])
    d_row['dataOrMC'] = pieces[-1]
    d_row['filename'] = filename
            
    df = df.append(d_row, ignore_index=True)

print(df)
df.to_csv('ledger.csv')