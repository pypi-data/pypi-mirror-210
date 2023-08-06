from os.path import basename, exists
import bisect
from pathlib import Path
import requests

def yld1():
    for i in range(0,5):
        yield i

def yld():
    yield from yld1()


def yld0():
    yield from (f"this is a test: {i}" for i in yld())

for i in yld0():
    print(i)

exit()
r = requests.get('https://raw.githubusercontent.com/GiorgosXou/init.lua/main/init.lua', stream=True)
path = './file.txt'
with open(path, 'wb') as f:
    total_length = int(r.headers.get('content-length'))/1024
    for i, chunk in enumerate(r.iter_content(chunk_size=1024)): #expected_size=(total_length/1024) + 1): 
        if chunk:
            print(int((i+1)*100/total_length))
            f.write(chunk)
            f.flush()

exit()

def tst():
    return 3

def tst0(i):
    if i == 2:
        return
    yield tst()

a = tst()
print(a)
for i in tst0(2):
    print(i)

exit()

def __common_method(func, *args):
    output = func(*args)
    yield output
    return output

def test(a,b,c):
    return a+b

def yield_func(tst): #Download
    for i in range(0,5):
        yield from __common_method(test, tst,1,2)
    return True

def funct2(tst): # instruction
    yield from yield_func(tst)


def funct():
    for i in range(0,10):
        yield from funct2(i)



for i in funct(): #debloat
    print(i)

exit()
response = requests.get(f'https://f-droid.org/api/v1/packages/org.fdroid.fdroid').json().get('suggestedVersionCode', None)
print(response)

a = [2,2]
assert a, 'no a'
def test(file):
    return basename(file).split('.')[0]

def debloat():
    for file in Path('/home/xou/Desktop/xou/notes/').rglob('*.md'):
        yield test(file)

# for f in debloat():
#     print(f)

from github import Github
from github.GithubException import UnknownObjectException

g = Github()
repo = g.get_repo("GiorgosXou/TUIFIManager")
stars = repo.stargazers_count
contents = repo.get_contents("TUIFIManager")
print(stars)
print(contents)



print(exists('home/xou'))
print(exists('/home/xou'))


def get_available_repos():
    pairs = [(10,'a'), (4,'c'), (1,'d'), (7,'b')]
    repos = []
    for repo_line in pairs:
        bisect.insort_left(repos, (repo_line[0], repo_line[1]), key=lambda x: -x[0])

    print(repos)

get_available_repos()

try:
    content = repo.get_contents('TUIFIManager/TUIFIProfile.aspy')
except UnknownObjectException as e:
    content = None

print(content)

print(g.get_repo('tst/asd'))
