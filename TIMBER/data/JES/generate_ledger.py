import glob, pandas

def get_run_block(sData,sMC):
    out, i = '', 0
    lData = list(sData.replace('DATA','MC'))
    while i < len(sMC):
        if sMC[i] == lData[i]:
            i+=1
        else:
            out+=lData.pop(i)

    return out.replace('_','').replace('Run','')

_columns = ['tag','ver','year','ULflag','dataOrMC','filename']

df = pandas.DataFrame(columns=_columns)

# Work with MC first to avoid dealing with runs
for filename in glob.glob('*MC.tar.gz'):
    pieces = filename.split('.')[0].split('_')

    if len(pieces) > 3:
        pieces[0] = pieces[0]+'_'+pieces.pop(1)
    elif len(pieces) > 4:
        raise IndexError('Expected at most 3 underscores ("_") in tarball names but found something different (%s). Algorithm assumes at most 3 underscores.'%filename)

    APVflag = True if 'APV' in pieces[0] else False

    d_row = {c:None for c in _columns}

    d_row['tag']      = pieces[0]
    d_row['ver']      = pieces[1]
    d_row['ULflag']   = True if 'UL' in d_row['tag'] else False
    d_row['dataOrMC'] = 'MC'
    d_row['filename'] = filename
    d_row['year']     = '20' + (d_row['tag'][-5:] if APVflag else d_row['tag'].split('_')[0][-2:])

    df = df.append(d_row, ignore_index=True)

print (df)

# For each of the new rows, find the corresponding data files, parse for info, and make new rows
MCdf = df.copy(deep=True) # Make copy so we don't modify what we are looping over by accident
for MCrow in MCdf.itertuples():
    files_to_grab = '%s%s%s_DATA.tar.gz'%(MCrow.tag, '_*' if MCrow.ULflag else '*_', MCrow.ver)
    print files_to_grab

    for filename in glob.glob(files_to_grab):
        if 'APV' in MCrow.filename and 'APV' not in filename:
            continue
        for letter in get_run_block(filename, MCrow.filename):
            d_row = {item[0]:item[1] for item in MCrow._asdict().items() if item[0] != 'Index'}
            d_row['dataOrMC'] = letter
            d_row['filename'] = filename
            df = df.append(d_row, ignore_index=True)

print(df)
df.to_csv('ledger.csv')