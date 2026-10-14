"""Convert first-model PDB C-alpha coordinates to the explicit ensemble schema."""
import argparse
import json
from pathlib import Path
from tool import analyze

def parse_pdb(text, ident):
    residues={}
    for line in text.splitlines():
        if line.startswith('ENDMDL'):
            break
        if not line.startswith('ATOM  ') or line[12:16].strip() != 'CA':
            continue
        altloc=line[16:17].strip()
        key=f"{line[21:22].strip() or '_'}:{line[22:26].strip()}:{line[26:27].strip()}"
        name=line[17:20].strip()
        coordinates=[float(line[30:38]),float(line[38:46]),float(line[46:54])]
        priority=(altloc != '', altloc != 'A', altloc)
        if key not in residues or priority < residues[key][0]:
            residues[key]=(priority,name,coordinates)
        elif priority == residues[key][0]:
            raise ValueError('Duplicate C-alpha at the same residue and altloc: '+key)
    if len(residues)<3:
        raise ValueError('Need at least 3 C-alpha residues')
    return {'id':ident,'residue_keys':list(residues),
            'residue_names':[r[1] for r in residues.values()],
            'coordinates':[r[2] for r in residues.values()]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pdbs',type=Path,nargs='+')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    data={'data_kind':'user-supplied PDB structures; coordinate correspondence required',
          'models':[parse_pdb(path.read_text(),path.name) for path in args.pdbs]}
    analyze(data) # Validate map equality before writing an apparently usable file.
    args.output.write_text(json.dumps(data,indent=2)+'\n')

if __name__=='__main__':
    main()
