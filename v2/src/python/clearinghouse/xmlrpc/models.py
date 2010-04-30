from django.db import models
import os
import binascii

class PasswordXMLRPCClient(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=3072,
        default=lambda: binascii.b2a_qp(os.urandom(1024)))
    max_password_age = models.IntegerField(
        'Maximum password age in days', default=60)
    password_timestamp = models.DateField(auto_now_add=True)
    url = models.URLField("XML-RPC Server URL", max_length=1024,
                          verify_exists=True)
    
    verify_ca = models.BooleanField("Verify the CA in SSL connections?",
                                    default=True)
    
    def __init__(self, *args, **kwargs):
        super(PasswordXMLRPCClient, self).__init__(*args, **kwargs)
        
    def __getattr__(self, name):
        if name == "proxy":
            from xmlrpclib import ServerProxy
            from clearinghouse.utils import PyCURLSafeTransport
            from django.conf import settings
            from datetime import timedelta, date
            
            if self.verify_ca:
                self.proxy = ServerProxy(
                    self.url, PyCURLSafeTransport(
                        username=self.username,
                        password=self.password,
                        ca_cert_path=settings.XMLRPC_TRUSTED_CA_PATH))
            else:
                self.proxy = ServerProxy(
                    self.url, PyCURLSafeTransport(
                        username=self.username,
                        password=self.password,
                    ))
            
            # if the password has expired, it's time to set a new one
            max_age = timedelta(days=self.max_password_age)
            if self.password_timestamp + max_age >= date.today():
                self.proxy.change_password(binascii.b2a_qp(os.urandom(1024)))
                
            return self.proxy
        else:
            return getattr(self.proxy, name)

    def install_trusted_ca(self):
        '''
        Add the CA that signed the certificate for self.url as trusted.
        '''
        import ssl
        import urlparse
        import subprocess
        from django.conf import settings
        
        # parse the url
        res = urlparse.urlparse(self.url)
        port = res.port or 443
        
        # get the PEM-encoded certificate
        cert = ssl.get_server_certificate((res.hostname, port))
        
        # dump it in the directory, and run make
        with open(os.path.join(settings.XMLRPC_TRUSTED_CA_PATH,
                               res.hostname+".ca.cert"),
                 'w') as cert_file:
            cert_file.write(cert)
        
        subprocess.call(['make', '-C', settings.XMLRPC_TRUSTED_CA_PATH])

