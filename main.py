from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import time
import os
import logging
from fastapi.responses import StreamingResponse
from typing_extensions import override
from openai import AssistantEventHandler
# Initialize OpenAI client
client = OpenAI(
  api_key=os.environ.get("OPENAI_API_KEY"),
)
app = FastAPI()
load_dotenv()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Hardcoded Assistant and Thread IDs
assistant_id = "asst_fKYP8oJNpPFeZJPC3F2ZZAXg"  # Replace with your assistant ID
thread_id = "thread_DneaN7SD9pYex38Z1Avt7dcj"  # Replace with your thread ID

class Message(BaseModel):
    content: str

class EventHandler(AssistantEventHandler):    
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
      
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)   

def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """
    Waits for a run to complete and prints the elapsed time.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                return response
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)

@app.get("/history/")
async def fetch_history_from_assistant():
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        history = []
        # Initialize variables to store the user message and assistant response
        user_message = None
        assistant_response = None

        for msg in messages.data:
            if msg.role == "user":
                # If there's an existing user message, save it with the current assistant response
                if user_message is not None:
                    history.append({"user_message": user_message, "assistant_response": assistant_response})
                
                # Update user message and reset assistant response
                user_message = msg.content[0].text.value
                assistant_response = None

            elif msg.role == "assistant":
                # Update assistant response when an assistant message is found
                assistant_response = msg.content[0].text.value

        # Append the last user-assistant pair to history, if exists
        if user_message is not None:
            history.append({"user_message": user_message, "assistant_response": assistant_response})
        
        return {"history": history}
    except Exception as e:
        logging.error(f"Error fetching history from assistant: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/history/")
async def post_history():
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        history = []
        user_message = None
        assistant_response = None

        for msg in messages.data:
            if msg.role == "user":
                if user_message is not None:
                    history.append({"user_message": user_message, "assistant_response": assistant_response})
                user_message = msg.content[-1].text.value
                assistant_response = None

            elif msg.role == "assistant":
                assistant_response = msg.content[-1].text.value

        if user_message is not None:
            history.append({"user_message": user_message, "assistant_response": assistant_response})

        # Reverse the history list to have the most recent messages first
        history.reverse()

        return {"history": history}
    except Exception as e:
        logging.error(f"Error fetching history from assistant: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    

@app.post("/chat")
async def chat(message: Message):
    try:
        # Create a message in the thread
        user_message = client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=message.content
        )
        
        # Run the assistant to process the message
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions = """
You are an assistant for a language school. Follow these guidelines to respond accurately in the language the user speaks. If the user changes their language, adapt and respond in the new language. Here are the instructions:

1. If a user asks about **changing the level of their class**, inform them that they need to send a ticket through the portal addressed to the 'Academics' department with the category 'Level Change,' and include the reason for the change in the description.
   
2. For questions about **retaking a test**, let them know that they need to send a ticket to 'Academics' under the category 'Test,' and that they can only retake the test within one week of missing it.

3. If asked about **replacing a missed class**, explain that missed classes are counted as absences unless the user took a full week of holidays.

4. For inquiries about the required **level for Business or Digital Marketing classes**, state that users need to be at level 5 to fully understand the content.

5. If a user asks about a **refund for canceling accommodation**, inform them that there is a two-week penalty for cancellation. They need to send a ticket to 'Accommodation' under the category 'Refund,' explaining the reason for the cancellation.

6. When asked about **extending accommodation**, advise them to send a ticket requesting an extension, and the responsible department will provide the exact cost, which varies by hotel and room type. Mention that the minimum extension is four weeks.

7. If someone asks how to **change their classes**, instruct them to send a ticket to 'Admissions' with the category 'Class Change.' If they want to change the class schedule, they should follow the same steps, changing the category to 'Class Schedule Change,' and include their preferred new schedule in detail, noting that changes are subject to availability.

8. Explain that there is **no cost for changing the course intensity**, but the number of weeks will change based on their request.

9. If asked what it means if a course is **intensive**, mention that it involves two classes per day, and the total course duration is halved.

10. Clarify that users can switch from an **intensive to a semi-intensive course**, which will double the remaining number of weeks.

11. Inform users that a **complete level lasts 12 weeks**.

12. Provide the **prices for books**: 220 dirhams for General English and 150 dirhams for Business.

13. If asked whether a **book is needed for Speaking class**, state that it is not required.

14. If a user is unable to **change their class**, explain that the groups may be full for that level this week, and they might have to wait until the end of the week when space may open up.

15. When asked about the number of **campuses**, inform them that there are two: one in Mazaya and one in Wollongong.

16. Explain that students can **transfer to another country** to continue their course, such as to a campus in London.

17. Provide details about **job search assistance** available in Dubai, including CV workshops, interview preparation, and job postings in the school's WhatsApp group.

18. For questions on how to **resume classes**, instruct users to send a ticket to 'Sales' with the category 'Return to Class,' mentioning their previous level and unit and when they want to return.

19. If a user wants to **pause their course**, they need to send a ticket to 'Sales' with the category 'Pause Course,' including the reason. Remind them they have six months to resume.

20. Explain the **options if a user cannot continue studying**, such as pausing the course for up to six months or transferring it to an immediate family member.

21. For questions about **payment methods for extending the course**, provide information on using an international card with a 3.5% fee, a local card with a 2.5% fee, or cash on the 15th floor.

22. Direct users to the 15th floor behind reception to **make payments for social activities**.

23. Inform users that they can learn about **social activities** in the portal under 'Social Activities' or in the WhatsApp group.

24. Provide instructions on how to **reach the school** if they miss the accommodation bus, based on their location.

25. For **visa cancellations**, guide users to send a ticket to the 'Visas' department with the category 'Visa Cancellation,' describing their reason. It takes 10 to 15 business days to process.

26. For **visa extensions**, users need to send a ticket to the 'Visas' department stating their desire and reason to extend it.

27. If someone cannot **access their portal**, advise them to use their registered email and enter their birthdate as their password. If issues persist, they should contact via WhatsApp.

28. Provide instructions on how to **reach biometric exams** when they collect documents from the Visa team.

29. Direct users to the reception on the 36th floor to **print documents**.

30. If someone cannot **upload their speaking test**, advise them to refresh the page and try again or send a voice message via WhatsApp.

31. Confirm that there is **Wi-Fi at Wollongong**; the network name is ES Dubai and the password is 24712471.

32. For inquiries about the **nationality of teachers**, mention that most are from the UK, America, and Ireland.

33. Explain the requirements to receive a **certificate of completion**, including attending at least 10 units of a level, maintaining 80% attendance, and achieving a grade above 80 in exams.

34. Clarify that vacations are only available weekly, and if they attend even one class, they are not eligible for the vacation week.

35. If a user hasn't received a response to their ticket and cannot open another one in the same department, reassure them that responses typically take 24 to 48 hours if the ticket is not closed.

36. List the **courses offered**: General English, Business, Speaking, Digital Marketing, IELTS, and Academic English.

37. Confirm that classes are currently **100% in-person and held Monday to Friday**.

Provide responses based on this information and do not generate answers that deviate from these guidelines."
"""

        )
        
        # Wait for the run to complete and fetch the assistant's response
        response_text = wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)
        
        return {"response": response_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


