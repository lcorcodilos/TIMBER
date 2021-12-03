import pandas, glob

_columns = ['year','ULflag','variation','nbins','filename']

_xsec_variation = {
    "66000ub":"down",
    "69200ub":"nominal",
    "72400ub":"up"
}

df = pandas.DataFrame(columns=_columns)

for ULflag in [True,False]:
    d_row = {c:None for c in _columns}
    if ULflag:
        prepend = 'UltraLegacy/'
    else:
        prepend = 'Preliminary/'
    
    for filename in glob.glob(prepend+'*.root'):
        pieces = filename.split('.')[0].split('-')

        if 'preVFP' in pieces:
            APVflag = True
            pieces.pop(pieces.index('preVFP'))
        elif 'postVFP' in pieces:
            APVflag = False
            pieces.pop(pieces.index('postVFP'))
        else:
            APVflag = None

        if pieces[4] == '80000ub':
            continue
            
        d_row['year'] = pieces[3] + ('APV' if APVflag else '')
        d_row['ULflag'] = ULflag
        d_row['variation'] = _xsec_variation[pieces[4]]
        d_row['nbins'] = int(pieces[5].replace('bins',''))
        d_row['filename'] = filename

        if d_row['year'] == '2016' and d_row['ULflag'] and APVflag == None:
            continue

        df = df.append(d_row, ignore_index=True)

pandas.set_option('display.max_colwidth', 1000)
print (df)
df.to_csv('ledger.csv')