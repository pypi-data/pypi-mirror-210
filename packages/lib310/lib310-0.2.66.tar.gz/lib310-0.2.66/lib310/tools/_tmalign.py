import os
import pathlib
import subprocess


def tm_align(pdb_file_1, pdb_file_2,out_dir):
    import os
    import subprocess
    url = 'https://zhanggroup.org/TM-score/TMscore.cpp'

    if (os.path.exists(r'TMalign')) == False:
        import requests
        r = requests.get(url, allow_redirects=True)
        open('TMalign.cpp', 'wb').write(r.content)
        print(subprocess.getoutput('g++ -O3 -ffast-math -lm -o TMalign {s}'.format(s='TMalign.cpp')))
    out_name = '{}TO{}'.format(pdb_file_1[:4], pdb_file_2[:4])
    batcmd = './TMalign {file1} {file2} -o {out_dir}/TM.{out_name}.sup -m {out_dir}/matrix{out_name}.txt'.format(file1=pdb_file_1,
                                                                                             file2=pdb_file_2,
                                                                                             out_name=out_name,
                                                                                             out_dir=out_dir)
    result = subprocess.getoutput(batcmd)
    return result



def tm_score( pdb_file_1,pdb_file_2,out_dir):
    import os
    import subprocess
    url = 'https://zhanggroup.org/TM-score/TMscore.cpp'

    if (os.path.exists(r'TMalign')) == False:
        import requests
        r = requests.get(url, allow_redirects=True)
        open('TMscore.cpp', 'wb').write(r.content)
        print(subprocess.getoutput('g++ -O3 -ffast-math -lm -o TMscore {s}'.format(s='TMscore.cpp')))
    # out_name = '{}TO{}'.format(pdb_file_1[:4], pdb_file_2[:4])
    batcmd = './TMscore {file1} {file2} '.format(file1=pdb_file_1,
                                                                                             file2=pdb_file_2,
                                                                                         )
    result = subprocess.getoutput(batcmd)
    return result