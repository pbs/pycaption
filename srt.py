from pycaption import BaseReader, BaseWriter

class SRTReader(BaseReader):
    def read(self, content, lang='en'):
        inlines = content.splitlines()
        i = 0
        subdata = []
                
        def srt2micro(stamp):
            timesplit = stamp.split(':')
            secsplit = timesplit[2].split(',')
            microseconds = int(timesplit[0]) * 3600000000 + int(timesplit[1]) * 60000000 \
            + int(secsplit[0]) * 1000000 + int(secsplit[1]) * 1000
            return microseconds
            
        while i < len(inlines):
            try:
                int(inlines[i])
            except:
                break
            
            j = i + 1
            while j < (len(inlines) + 1):
                try:
                    nid = int(inlines[j])
                    break
                except:
                    j += 1
            
            timing = inlines[i+1].split('-->')
            start = srt2micro(timing[0].strip(' \r\n'))
            end = srt2micro(timing[1].strip(' \r\n'))
            text = []
            first = True
            for line in inlines[i+2:j-1]:
                if not first:
                    text += [{'type': 'break', 'content': ''}]
                text += [{'type': 'text', 'content': line}]
                first = False
            
            subdata += [[start, end, text, {}]]
            i = j
        
        return {'captions': {lang: subdata}, 'styles': {}}

class SRTWriter(BaseWriter):
    def write(self, captions):
        srt = ''
        for lang in captions['captions']:
            count = 1
            srt += '\n"%s" SRT Captions\n' % lang
            for sub in captions['captions'][lang]:
                srt += '%s\n' % count
                start = '0' + str(datetime.timedelta(milliseconds=(int(sub[0] / 1000))))[:11]
                end = '0' + str(datetime.timedelta(milliseconds=(int(sub[1] / 1000))))[:11]
                timestamp = '%s --> %s\n' % (start, end)
                srt += timestamp.replace('.', ',')
                for line in sub[2]:
                    if line['type'] == 'text':
                        srt += '%s ' % line['content']
                    elif line['type'] == 'break':
                        srt += '\n'
                srt += '\n\n'
                count += 1
        return srt[:-2]