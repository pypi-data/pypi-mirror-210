# send mail
#   SQL version

from pfstools import SqlCnx


def send_mail(recipients,subject, msg_body, **kwargs):
    allowed_args = { 
        'recipients',
        'subject',
        'body',
        'profile_name',  
        'copy_recipients', 
        'blind_copy_recipients', 
        'from_address', 
        'reply_to', 
        'body_format', 
        'importance', 
        'sensitivity', 
        'file_attachments', 
        'query', 
        'execute_query_database', 
        'attach_query_result_as_file', 
        'query_attachment_filename', 
        'query_result_header', 
        'query_result_width', 
        'query_result_separator', 
        'exclude_query_output', 
        'append_query_error', 
        'query_no_truncate', 
        'query_result_no_padding', 
        'mailitem_id', }
    mail_server = kwargs.get('mail_server', 'MCPFSSWDB002')
    mailer = SqlCnx(server = mail_server, db = 'master')
    args = {'recipients' : recipients, 'subject' : subject ,  'body' : msg_body} | kwargs
    arg_list = ',\n'.join([f"     @{kw} = '{args[kw]}' " for kw in allowed_args.intersection(args.keys())])
    send_sql = f"""
                    EXEC msdb.dbo.sp_send_dbmail 
                        {arg_list}
                """

    #print(send_sql)
    return mailer.exec(send_sql)

# send mail
#   SMTP version
