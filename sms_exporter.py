import lxml.etree as ET
from xml.dom import minidom

def export_sms_to_xml(sms_data, output_xml):
    root = ET.Element("smses")
    for sms in sms_data:
        print("SMS", sms['ROWID'], sms["sender"], sms['f_date'], sms['text'])
        sms_element = ET.SubElement(root, "sms")
        sms_element.set("address", sms["sender"])
        sms_element.set("date", str(sms["u_date"]))
        sms_element.set("rowid", str(sms["ROWID"]))
        sms_element.set("type", sms["type"])
        sms_element.set("body", sms["text"] if sms["text"] else "")
        sms_element.set("read", "1")
        sms_element.set("status", "-1")
    
    pretty_xml_as_str = ET.tostring(root, encoding='utf-8', pretty_print=True).decode('utf-8')

    with open(output_xml, 'w', encoding='utf-8') as file:
        file.write(pretty_xml_as_str)

def export_mms_to_xml(mms_data, output_mms_xml):
    root = ET.Element("smses")
    for sms in mms_data:
        print("MMS", sms['ROWID'], sms["sender"], sms['f_date'], sms['transfer_name'] + " -> " + sms["ori_filename"])
        mms_element = ET.SubElement(root, "mms")
        mms_element.set("retr_st", 'null')
        mms_element.set("date", str(sms["u_date"]))
        mms_element.set("ct_cls", 'null')
        mms_element.set("sub_cs", 'null')
        mms_element.set("read", '1')
        mms_element.set("ct_l", 'null')
        mms_element.set("tr_id", 'null')
        mms_element.set("st", 'null')
        mms_element.set("msg_box", sms["type"])
        mms_element.set("address", sms["sender"])
        mms_element.set("m_cls", "personal")
        mms_element.set("d_tm", 'null')
        mms_element.set("read_status", 'null')
        mms_element.set("ct_t", 'application/vnd.wap.multipart.related')
        mms_element.set("retr_txt_cs", 'null')
        mms_element.set("d_rpt", '129' if sms["type"] == '2' else 'null')
        mms_element.set("m_id", sms["attachment_guid"])
        mms_element.set("date_sent", str(int(sms["u_date"]/1000)))
        mms_element.set("seen", '1')
        mms_element.set("m_type", '128')
        mms_element.set("v", '19')
        mms_element.set("exp", 'null')
        mms_element.set("pri", '129')
        mms_element.set("rr", '129')
        mms_element.set("resp_txt", 'null')
        mms_element.set("rpt_a", 'null')
        mms_element.set("locked", '0')
        mms_element.set("retr_txt", 'null')
        mms_element.set("resp_st", '128')
        mms_element.set("m_size", str(sms["total_bytes"]))
        parts_element = ET.SubElement(mms_element, "parts")
        part_element = ET.SubElement(parts_element, "part")
        part_element.set("seq", '0')
        part_element.set("ct", sms["mime_type"])
        part_element.set("name", 'null')
        part_element.set("chset", '106')
        part_element.set("cd", 'null')
        part_element.set("fn", sms["ori_filename"])
        part_element.set("cid", "&lt;" + sms["attachment_guid"] + "&gt;")
        part_element.set("cl", sms["ori_filename"])
        part_element.set("ctt_s", 'null')
        part_element.set("ctt_t", 'null')
        part_element.set("text", 'null')
        part_element.set("data", sms["file_data"])
    
    tree = ET.ElementTree(root)
    xml_str = ET.tostring(root, encoding='utf-8')
    parsed_str = minidom.parseString(xml_str)
    pretty_xml_as_str = parsed_str.toprettyxml(indent="  ")
    
    with open(output_mms_xml, 'w', encoding='utf-8') as file:
        file.write(pretty_xml_as_str)
