from subprocess import run, PIPE

cmd = input("Command: ")

process = run(cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True)

print()
print("STDOUT: \n", process.stdout, sep='\n')
print()
print("STDERR: \n", process.stderr, sep='\n')
print()
