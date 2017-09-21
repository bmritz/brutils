import yaml, uuid

class GDMetaData(dict):
    """
    This holds the metadata for the GDPlot object
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)    
        if 'other' not in self:
            self['other'] = dict()
        
        # set up the filenames based on the uuid
        # ok for now -- find a better way to update on __init__
        try:
            self.uid = self['uuid']
        except KeyError:
            try:
                self.uid = self['other']['uuid']
            except KeyError:
                self.get_new_uuid(update_meta_uid=False)
        self.update_meta_uid()
        self['showtitle'] = True
        self.has_standard_text = False

    def update_meta_uid(self):
        """update the filenames with the latest uid in the metadata"""
        self['other']['yaml'] = self.uid+'.yaml'
        self['name'] = self.uid+".svg"
        self['uuid'] = self.uid
        self['pretext'] = 'UUID: %s' % self.uid
        self['export'] = self.uid+".png"
        self['file'] = self.uid+".json"
        return self

    def get_new_uuid(self, update_meta_uid=True):
        """
        Get a new uuid to save and not overwrite a file
        """
        self.uid = str(uuid.uuid1())
        if update_meta_uid:
            self.update_meta_uid()
        return self.uid

    def conform_to_GD(self):
        """
        Conform the metadata to the standards expected by GD
        """
        gd_labels = ['index', 'name', 'title', 'text', 
                    'labels', 'rank', 'export', 'file', 
                    'pretext', 'id', 'showtitle', 'family', 'other']
        for k, v in self.items():
            if k not in gd_labels:
                self['other'].update({k: self.pop(k)})
        return self

    def to_yaml(self):
        """
        return a yaml string of the dict
        """
        return yaml.dump(dict(self))

    def to_yaml_file(self, filename):
        """
        dump the yaml to a file
        """
        with open(filename, 'w') as f:
            yaml.dump(dict(self), f)

    def recurse_get(self, key, default=None):
        """
        Try to get the key in the dict housed in the "other" key first, then look for it in the top level,
        then return default if still not found
        """

        return self['other'].get(key, self.get(key, default))

    def GD_standard_text(self):
        """
        THINK ABOUT DIVIDING THIS INTO TWO FUNCTIONS -- one takes user, title, created as params,
        The other calls that method with the params populated by its own metadata - could have this throw error if metadata is not there
        Make the 'text' standardized based off of other metadata
        
        text: |         # line1
        <title>         # line2
        ---             # line3
        (uploaded <timestamp> by <user>)
        
        <optional description>
        
        ```python
        <function code>
        ```
        """
    
        user = self.recurse_get('user', 'No User Information')
        title = self.get('title', "Untitled")
        created = self.recurse_get('created', 'No Date Information')

        text_lines = [" |"]                      # line1
        text_lines.append("   "+title)  # line2
        text_lines.append("   ---")             # line3
        text_lines.append("   *(uploaded on: "+created+", by: "+user+")*")
        
        # take this out for now because it recursively appends when dowloading from GD
        #if 'text' in self and (self.has_standard_text is False):
        #    text_lines.append("")
        #    text_lines.append("   "+self['text'])

        src = self.recurse_get('function_source')

        if src:
            text_lines.append("")
            text_lines.append("   ```python\n")
            text_lines.append("   "+"\n   ".join(src.split("\n")))
            text_lines.append("   ```")
    
        self['text'] = "\n".join(text_lines)
        self.has_standard_text = True
        return self