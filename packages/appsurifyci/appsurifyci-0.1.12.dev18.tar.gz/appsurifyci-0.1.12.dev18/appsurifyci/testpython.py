import re
import subprocess


COMMAND_COMMIT = "git show --reverse --first-parent --raw --numstat --abbrev=40 --full-index -p -M --pretty=format:'Commit:\t%H%nDate:\t%ai%nTree:\t%T%nParents:\t%P%nAuthor:\t%an\t%ae\t%ai%nCommitter:\t%cn\t%ce\t%ci%nMessage:\t%s%n' {}"

RE_COMMIT_HEADER = re.compile(
    r"""^Commit:\t(?P<sha>[0-9A-Fa-f]+)\nDate:\t(?P<date>.*)\nTree:\t(?P<tree>[0-9A-Fa-f]+)\nParents:\t(?P<parents>.*)\nAuthor:\t(?P<author>.*)\nCommitter:\t(?P<committer>.*)\nMessage:\t(?P<message>.*)?(?:\n\n|$)?(?P<file_stats>(?:^:.+\n)+)?(?P<file_numstats>(?:.+\t.*\t.*\n)+)?(?:\n|\n\n|$)?(?P<patch>(?:diff[ ]--git(?:.+\n)+)+)?(?:\n\n|$)?""",
    re.VERBOSE | re.MULTILINE)
output = "Commit:    39893b96f2266881f28c51e33b64009774fafb2d\n Date:    2023-04-10 16:51:21 +0000\n Tree:    e42ea2ed893e8142c6dde955fcc582f082a6c014\n Parents:    a3dec2a341252993040578cd6f47c038164772ce 66ced5e022152a8a88518a95a0841313028cd5e2\n Author:    Evan Knox    eknox@kinaxis.com    2023-04-10 16:51:21 +0000\n Committer:    Evan Knox    eknox@kinaxis.com    truenMessage:    Pull request #48514: Part 1 - Refactor the EditRangeDialog\n :100644 100644 8ceb931d8c05b8a516b45db008a36e34563c19f8 5f84113ec9bbac11c92fcf1f2d0da773deb9adaa M    RapidResponse/Web\n Server/Web/app/packages/worksheet-react/src/ag-grid/components/EditRangeDialog.tsx\n :000000 100644 0000000000000000000000000000000000000000 f3a2fbd2460f6a30982ebbf8b8026ea3439f49df A    RapidResponse/Web\n Server/Web/app/packages/worksheet-react/src/ag-grid/components/test/EditRangeDialog.jest.tsx\n" 



def execute(commandLine):
    try:
        process = subprocess.Popen(commandLine, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out = process.stdout.read().strip().decode("UTF-8", errors='ignore')
        error = process.stderr.read().strip().decode("UTF-8", errors='ignore')

        if error:
            process.kill()
            raise Exception(error)
    except Exception as ex:
        print(ex)
    return out


sha = "72c4da75d7c71115d4770a6552098456ca20263b"
commit_cmd = COMMAND_COMMIT.format(sha)
commit_cmd = commit_cmd.replace('\'', '\"')
commit_cmd = commit_cmd.replace('\t', '%x09')
print('Commit command {}'.format(commit_cmd))
#output = execute(commit_cmd)


commit_header = RE_COMMIT_HEADER.findall(output)[0]
print(commit_header)
print("#####################################")
print("#####################################")
#print(output)