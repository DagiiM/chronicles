import openai
from decouple import config
import time
from tenacity import retry, stop_after_delay, wait_fixed

openai.api_key = config('OPENAI_API_KEY')

@retry(stop=stop_after_delay(60), wait=wait_fixed(1))
def generate_text(prompt,max_tokens=200):
  response = None
  while response is None:
    try:
        response = openai.ChatCompletion.create(
        max_tokens=max_tokens,
        model="gpt-3.5-turbo",
        messages=[
              {"role": "system", "content": "You are a consultant doctor. Be as precise as possible. You are always replying to a patient. You work at Equity Afia Healthy Clinic. You cannot use more than 500 words. use bullets where possible."},
              {"role": "user", "content": prompt},
          ]
        )
    except openai.error.APIError as e:
        if e.status == 429 and 'Please include the request ID' in e.message:
            request_id = e.message.split('Please include the request ID ')[-1].split(' in your message.')[0]
            print(f'Retrying request {request_id}')
            request = openai.api_resources.Request.get(request_id)
            while request.status == 'pending':
                time.sleep(1)
                request = openai.api_resources.Request.get(request_id)
            response = openai.api_resources.ChatCompletion.get(request.response['id']).choices[0]
        elif e.status == 403:
            print('API key unauthorized')
            return None
        elif e.status == 402:
            print('Ran out of credits')
            return None
        else:
            raise e

  response = response.choices[0].message.content.strip().replace('\n', '<br>')
  return response
