import glob, pandas

_columns = ['tag','ver','year','ULflag','APVflag','dataOrMC','filename']

df = pandas.DataFrame(columns=_columns)

for filename in glob.glob('*.tar.gz'):
    pieces = filename.split('.')[0].split('_')

    if len(pieces) > 3:
        raise IndexError('Expected 2 underscores ("_") in tarball names but found something different (%s). Algorithm assumes 2 underscores.'%filename)

    d_row = {c:None for c in _columns}

    d_row['tag']      = pieces[0]
    d_row['ver']      = pieces[1]
    d_row['ULflag']   = True if 'UL' in d_row['tag'] else False
    d_row['APVflag']  = True if 'APV' in d_row['tag'] else False
    d_row['year']     = d_row['tag'][-5:-3] if d_row['APVflag'] else d_row['tag'][-2:]
    d_row['dataOrMC'] = 'MC'
    d_row['filename'] = filename
            
    df = df.append(d_row, ignore_index=True)

print(df)
df.to_csv('ledger.csv')