import src.sms_api_guru as api

api.set_key("1234")

result = api.send_sms("+381690156360")
print(result)
#coderesult = tf.verifyCode("+381690156360", result)
#print(coderesult.valid)