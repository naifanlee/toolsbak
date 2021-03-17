import os, sys


src = sys.argv[1]
dst = 'csv_res'
os.system('rm -rf {}'.format(dst))
os.makedirs(dst)

for root, dirs, files in os.walk(src):
    if 'images' not in root:
        continue

    os.system('rm -rf images; ln -s {} images'.format(root))
    
    with open('list.txt', 'w') as f:
        f.write('\n'.join([fname.strip() for fname in files if fname.strip() != '']).strip())

    os.system('./run.sh')
    dst_path = os.path.join(dst, root.split('benchmark')[-1].lstrip('/')).replace('images', 'csv')
    os.makedirs(dst_path)
    os.system('mv *.csv {}'.format(dst_path))