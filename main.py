from backup_parser import parse_backup, parse_backup_paginated, get_mms_count
from sms_exporter import export_sms_to_xml, export_mms_to_xml

def main():
    backup_path = 'D:\\VMshare\\00008110-0012492A34E8401E'
    output_csv = 'output/sms.csv'
    output_sms_xml = 'output/sms.xml'
    page = 1
    output_mms_xml = f'output/mms.{page}.xml'
    
    total_page = get_mms_count(backup_path) // 100 + 1
    print(f"Total pages: {total_page}")
    for page in range(1, total_page + 1):
        mms_data = parse_backup_paginated(backup_path, page)
        export_mms_to_xml(mms_data, f'output/mms.{page}.xml')
    sms_data = parse_backup(backup_path)
    export_sms_to_xml(sms_data, output_sms_xml)
    # mms_data = parse_backup_mms(backup_path)
    # export_mms_to_xml(mms_data, output_mms_xml)

if __name__ == '__main__':
    main()
