import opennaas.geniv3 as gv3

import logging
logger = logging.getLogger("opennaas-geniv3-commands")


def create_urn_from_slice_name(sname):
    return 'urn:publicid:IDN+geni:gpo:gcf+slice+' + str(sname)


def verify_connectivity(address, port):
    func_ = verify_connectivity.__name__
    logger.debug("%s address=%s, port=%s" % (func_, address, port,))

    geni3c_ = gv3.GENI3Client(address, port)
    logger.debug("%s Geniv3Client successfully init" % (func_,))
    try:
        resp_ = geni3c_.getVersion()
        if geni3c_.isError(resp_):
            return "(OpenNaaS) AM error [%d]: %s" %\
                   (geni3c_.errorCode(resp_), geni3c_.errorMessage(resp_),)

    except Exception as e:
        return "(OpenNaaS) AM exception: %s" % (e,)

    return None


def list_available_resources(address, port):
    func_ = list_available_resources.__name__
    logger.debug("%s address=%s, port=%s" % (func_, address, port,))

    geni3c_ = gv3.GENI3Client(address, port)
    logger.debug("%s Geniv3Client successfully init" % (func_,))

    err_, resources_ = None, []
    try:
        resp_ = geni3c_.listResources(credentials=[gv3.TEST_CREDENTIAL], available=True)
        if geni3c_.isError(resp_):
            err_ = "(OpenNaaS) AM error [%d]: %s" %\
                   (geni3c_.errorCode(resp_), geni3c_.errorMessage(resp_),)
        else:
            resources_ = gv3.decode_list_resources(resp_.get('value'))

    except Exception as e:
        err_ = "(OpenNaaS) AM exception: %s" % (e,)

    return err_, resources_


def status_resources(address, port, slice_name):
    func_ = status_resources.__name__
    logger.debug("%s address=%s, port=%s, slice=%s" % (func_, address, port, slice_name))

    geni3c_ = gv3.GENI3Client(address, port)
    logger.debug("%s Geniv3Client successfully init" % (func_,))

    err_, resources_ = None, []
    try:
        urn_ = create_urn_from_slice_name(slice_name)
        resp_ = geni3c_.status(urns=[urn_], credentials=[gv3.TEST_CREDENTIAL])
        if geni3c_.isError(resp_):
            err_ = "(OpenNaaS) AM error [%d]: %s" %\
                   (geni3c_.errorCode(resp_), geni3c_.errorMessage(resp_),)
        else:
            resources_ = gv3.decode_status_resources(resp_.get('value').get('geni_urn'))

    except Exception as e:
        err_ = "(OpenNaaS) AM exception: %s" % (e,)

    return err_, resources_


def allocate_resource(address, port, slice_name, info):
    func_ = allocate_resource.__name__
    logger.debug("%s address=%s, port=%s, slice=%s, info=%s" %\
                 (func_, address, port, slice_name, info,))

    geni3c_ = gv3.GENI3Client(address, port)
    logger.debug("%s Geniv3Client successfully init" % (func_,))

    err_ = None
    try:
        urn_ = create_urn_from_slice_name(slice_name)
        resp_ = geni3c_.allocate(slice_urn=urn_, credentials=[gv3.TEST_CREDENTIAL],
                                 rspec=gv3.encode_allocate_resource(info))
        if geni3c_.isError(resp_):
            err_ = "(OpenNaaS) AM error [%d]: %s" %\
                   (geni3c_.errorCode(resp_), geni3c_.errorMessage(resp_),)

    except Exception as e:
        err_ = "(OpenNaaS) AM exception: %s" % (e,)

    return err_


def delete_slice(address, port, slice_name):
    func_ = delete_slice.__name__
    logger.debug("%s address=%s, port=%s, slice=%s" %\
                 (func_, address, port, slice_name,))

    geni3c_ = gv3.GENI3Client(address, port)
    logger.debug("%s Geniv3Client successfully init" % (func_,))

    err_ = None
    try:
        urn_ = create_urn_from_slice_name(slice_name)
        resp_ = geni3c_.delete(urns=[urn_], credentials=[gv3.TEST_CREDENTIAL])
        if geni3c_.isError(resp_):
            err_ = "(OpenNaaS) AM error [%d]: %s" %\
                   (geni3c_.errorCode(resp_), geni3c_.errorMessage(resp_),)

    except Exception as e:
        err_ = "(OpenNaaS) AM exception: %s" % (e,)

    return err_


def perform_operation(address, port, slice_name, command):
    func_ = perform_operation.__name__
    logger.debug("%s address=%s, port=%s, slice=%s, command=%s" %\
                 (func_, address, port, slice_name, command,))

    geni3c_ = gv3.GENI3Client(address, port)
    logger.debug("%s Geniv3Client successfully init" % (func_,))

    err_ = None
    try:
        urn_ = create_urn_from_slice_name(slice_name)
        resp_ = geni3c_.performOperationalAction(urns=[urn_], credentials=[gv3.TEST_CREDENTIAL],
                                                 action=command)
        if geni3c_.isError(resp_):
            err_ = "(OpenNaaS) AM error [%d]: %s" %\
                   (geni3c_.errorCode(resp_), geni3c_.errorMessage(resp_),)

    except Exception as e:
        err_ = "(OpenNaaS) AM exception: %s" % (e,)

    return err_
