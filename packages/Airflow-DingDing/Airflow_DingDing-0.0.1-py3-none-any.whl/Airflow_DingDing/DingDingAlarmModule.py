import requests

class DingDingAlarmModule():
    def send_error_dingding(access_token, message, context, msgtype='text'):
        task_id = context['task_instance'].task_id
        dag_id = context['task_instance'].dag_id
        exception = context['exception']

        final_message = message.format(task_id=task_id, dag_id=dag_id, exception=exception)

        dingding_url = "https://oapi.dingtalk.com/robot/send?access_token={access_token}"  # Replace with your Dingding webhook URL
        headers = {"Content-Type": "application/json"}
        payload = {"msgtype": msgtype, "text": {"content": final_message}}

        response = requests.post(dingding_url, json=payload, headers=headers)
        response.raise_for_status()