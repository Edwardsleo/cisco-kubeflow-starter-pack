import sys
import os

def usage():
    print("usage: python "+sys.argv[0]+" file.param layer_name paramx=value paramx=value...")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        usage()
        raise Exception("Error occurred!! More error details below %s\n" %sys.exc_info())

    file_name = sys.argv[1]
    layer_name = sys.argv[2]
    basename = os.path.splitext(file_name)[0]
    out_file_name = basename+"_patch.param"
    out_file = open(out_file_name, "w")
    params={}
    for i in range(3,len(sys.argv)):
        p = sys.argv[i].strip().split('=')
        if len(p) != 2:
            usage()
            raise ValueError("bad parameter: ", sys.argv[i])
        params[p[0]]=p[1]

    print(params)


    if not os.path.isfile(file_name):
        raise FileNotFoundError("File path {} does not exist. Exiting...".format(file_name))

    with open(file_name) as fp:
        for line in fp:
            largs = line.strip().split(' ')
            if (largs[0] == layer_name):
                print("patch   line:", line)
                for i in range(1,len(largs)):
                    if '=' in largs[i]:
                        p = largs[i].strip().split('=')
                        if p[0] in params:
                            largs[i] = p[0]+"="+params[p[0]]
                            print(p[0],"=",p[1],"->",largs[i])

                print("patched line:", ' '.join(largs))
                out_file.write(' '.join(largs))
            else:
                out_file.write(line)
        
    out_file.close()

