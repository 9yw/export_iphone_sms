import sqlite3
from hashlib import sha1
import base64
from resize_pic import resize_image

def parse_backup(backup_path):
    sms_db = f'{backup_path}/3d/3d0d7e5fb2ce288813306e4d4636395e047a3d28'
    conn = sqlite3.connect(sms_db)
    conn.row_factory = sqlite3.Row  # 设置 row_factory 属性
    cursor = conn.cursor()
    
    query = '''
    SELECT
        message.ROWID,
        SUBSTR(message.date, 1, 12) + 978307200000 as u_date,
        datetime(SUBSTR(message.date, 1, 9) + 978307200, 'unixepoch', 'localtime') as f_date,
        handle.id AS sender,
        is_from_me,
        CASE
            WHEN message.text = '' OR HEX(text) = 'EFBFBC' THEN NULL 
            ELSE message.text
        END AS text,
        REPLACE(attachment.filename, '~/Library', 'MediaDomain-Library') AS formatted_filename,
        transfer_name,
        attachment.guid as attachment_guid,
        attachment.mime_type,
        attachment.total_bytes
    FROM
        message
    JOIN
        handle ON message.handle_id = handle.ROWID
    LEFT JOIN
        message_attachment_join ON message.ROWID = message_attachment_join.message_id
    LEFT JOIN
        attachment ON message_attachment_join.attachment_id = attachment.ROWID
    WHERE
        message.text IS NOT NULL AND attachment.filename IS NULL
        -- message.ROWID = '189441'
    ORDER BY
        message.ROWID
    '''
    cursor.execute(query)
    sms_data = []
    def remove_invalid_xml_chars(text):
        if text:
            return ''.join(c for c in text if c.isprintable() and ord(c) <= 0x1FFFF)
            # return ''.join(c for c in text if c.isprintable() and ord(c) <= 0xFFFF)
        return text

    for row in cursor.fetchall():
        dic_row = dict(row)
        dic_row['type'] = '1'
        dic_row['MMS'] = False
        dic_row['text'] = remove_invalid_xml_chars(dic_row['text'])
        if dic_row['is_from_me'] == 0:
            dic_row['type'] = '1'
        else:
            dic_row['type'] = '2'
        sms_data.append(dic_row)
    # sms_data = []
    # rows = cursor.fetchall()
    # for row in rows:
    #     sms_data.append(dict(row))  # 将结果转换为字典并添加到列表中
    
    # print(sms_data)
    conn.close()
    return sms_data

def get_mms_count(backup_path):
    sms_db = f'{backup_path}/3d/3d0d7e5fb2ce288813306e4d4636395e047a3d28'
    conn = sqlite3.connect(sms_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
    SELECT
        COUNT(*)
    FROM
        attachment
    WHERE
        attachment.filename IS NOT NULL AND mime_type is NOT NULL
    '''
    cursor.execute(query)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def parse_backup_paginated(backup_path, page_number, page_size=100):
    sms_db = f'{backup_path}/3d/3d0d7e5fb2ce288813306e4d4636395e047a3d28'
    conn = sqlite3.connect(sms_db)
    conn.row_factory = sqlite3.Row  # 设置 row_factory 属性
    cursor = conn.cursor()
    
    offset = (page_number - 1) * page_size
    query = f'''
    SELECT
        message.ROWID,
        SUBSTR(message.date, 1, 12) + 978307200000 as u_date,
        datetime(SUBSTR(message.date, 1, 9) + 978307200, 'unixepoch', 'localtime') as f_date,
        handle.id AS sender,
        is_from_me,
        CASE
            WHEN message.text = '' OR HEX(text) = 'EFBFBC' THEN NULL 
            ELSE message.text
        END AS text,
        REPLACE(attachment.filename, '~/Library', 'MediaDomain-Library') AS formatted_filename,
        transfer_name,
        attachment_id,
        attachment.guid as attachment_guid,
        attachment.mime_type,
        attachment.total_bytes
    FROM
        message
    JOIN
        handle ON message.handle_id = handle.ROWID
    LEFT JOIN
        message_attachment_join ON message.ROWID = message_attachment_join.message_id
    LEFT JOIN
        attachment ON message_attachment_join.attachment_id = attachment.ROWID
    WHERE
        attachment.filename IS NOT NULL AND mime_type is NOT NULL
    ORDER BY
        message.ROWID
    LIMIT {page_size} OFFSET {offset}
    '''
    cursor.execute(query)
    mms_data = []
    for row in cursor.fetchall():
        dic_row = dict(row)
        dic_row['type'] = '1'
        if dic_row['formatted_filename']:
            dic_row['MMS'] = True
            file_size = dic_row['total_bytes']
            file_type = dic_row['mime_type']
            bak_filename = sha1(dic_row['formatted_filename'].encode()).hexdigest()
            try:
                with open(f'{backup_path}/{bak_filename[:2]}/{bak_filename}', 'rb') as file_stream:
                    file_data = file_stream.read()
                    # if file_size > 500 * 1024 and file_type in ['image/jpeg', 'image/png']:
                    #     # print(f"Resizing image {dic_row['attachment_id']} {dic_row['sender']} {dic_row['formatted_filename']} {file_type}")
                    #     file_data,file_size = resize_image(file_data, file_size, file_type)
                    #     print(f"Resized image {dic_row['attachment_id']} {dic_row['sender']} {dic_row['formatted_filename']} {file_type} {dic_row['total_bytes']} {file_size}")
                    file_data = base64.b64encode(file_data).decode('utf-8')
            except FileNotFoundError:
                with open('output/bad.txt', 'a') as bad_file:
                    bad_file.write(f"{dic_row['ROWID']},{dic_row['f_date']},{dic_row['sender']},{dic_row['formatted_filename']}\n")
                continue
            dic_row['file_data'] = file_data
            dic_row['total_bytes'] = file_size
            dic_row['ori_filename'] = dic_row['attachment_guid'] + '-' + dic_row['transfer_name']
        else:
            dic_row['MMS'] = False
        if dic_row['is_from_me'] == 0:
            dic_row['type'] = '1'
        else:
            dic_row['type'] = '2'
        mms_data.append(dic_row)
    conn.close()
    return mms_data