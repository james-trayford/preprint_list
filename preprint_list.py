import mailbox
import email.utils
import numpy as np
import os
import re
import glob
import email as em
import arxiv as arx
import sys
import codecs
import locale

# Wrap sys.stdout into a StreamWriter to allow writing unicode.
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

DIAGNOSTICS=True
WEIGHT = 1

if len(sys.argv) > 1:
    WEIGHT = float(sys.argv[1])
if len(sys.argv) > 2:
    DIAGNOSTICS=bool(int(sys.argv[2]))


def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
    
mbox = mailbox.Maildir(os.environ['HOME'] + "/Maildir/.INBOX.preprints" )

suggestions = []
weights = []
people = []
upeople = []
counts = []
picknum = []

for path in glob.glob(os.environ['HOME'] + "/Maildir/.INBOX.preprints/*/*"):
    f = file(path, 'r')
    email = f.read()

    email = re.sub('^>.*\n?', '', email, flags=re.MULTILINE)
    # print email
    # email = re.sub('<.*\n?', '', email, flags=re.MULTILINE)
    # print email
    name = email.split('From: ')[1].split('\n')[0]
    # print 'ID: ', name
    suggs = re.findall('( arXiv:20[0-9]{2}\.[0-9]{5} |^arXiv:20[0-9]{2}\.[0-9]{5})', email, flags=re.MULTILINE)
    suggs2 = re.findall('( http\S+20[0-9]{2}\.[0-9]{5}|^http\S+20[0-9]{2}\.[0-9]{5})', email, flags=re.MULTILINE)
    suggs3 = re.findall('(20[0-9]{2}\.[0-9]{5})', email, flags=re.MULTILINE)
    sugg  = '\n'.join(suggs+suggs2+suggs3)
    print suggs3
    suggunq = list(f7(np.array(re.findall('20[0-9]{2}\.[0-9]{5}', sugg, flags=re.MULTILINE))))
    
    ranks   = (np.arange(len(suggunq))+1.)**WEIGHT
    score   = ranks[::-1]/((ranks[::-1].sum()))
    # print name
    # print suggunq
    # print score
    
    suggestions += suggunq
    upeople.append(name)
    people += [name]*len(suggunq)
    weights += list(score)
    picknum += range(1,len(suggunq)+1)
    counts += [len(score)] * len(score)
    # e    print ranks, weights      
    
    f.close()

sarr = np.array(suggestions)
parr = np.array(people)
warr = np.array(weights)
rarr = np.array(picknum)
carr = np.array(counts)



total = []
peeps = []
iweight = []
icount = []
irank = []

for s in np.unique(sarr):
    total.append(np.sum(warr[sarr==s]))
    iweight.append(tuple(warr[sarr==s]))
    icount.append(tuple(carr[sarr==s]))
    irank.append(tuple(rarr[sarr==s]))
    peeps.append(tuple(parr[sarr==s]))

order = np.argsort(total)[::-1]



print '\n\nAttendees:'
print '\n'.join(['%s']*len(upeople))% tuple(upeople)
print '\n'

for s in order:
    print '========================================='
    #print 'Preprint: ', np.unique(sarr)[s], 
    p = arx.query(id_list=[np.unique(sarr)[s]])[0]
    print ''.join(p['title'].split('\n '))
    auths = p['authors']
    if len(auths) > 3:
        print auths[0] + ' et. al'
    else:
        print ', '.join(auths)
    print p['arxiv_url']
    if DIAGNOSTICS:
        print ' - - - - - - - - - - - - - - - - - - - - '
        print 'Total score: %.3f' % total[s]
        peepord = np.argsort(iweight[s])[::-1]
        for i in peepord:
            print '\t ', peeps[s][i], 'score: %.3f (%d of %d)'%(iweight[s][i], irank[s][i], icount[s][i])
    print '\n'

# mbox.lock()
# for message in mbox:
#     # print "- [%s] %s:  \"%s\"" % ( message['date'], message['from'], message['subject'] )
#     print message['from'].split(' ')[0]
#     print message.get_message()

    

# mbox.close()
