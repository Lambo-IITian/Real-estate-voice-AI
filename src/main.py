# src/main.py
import time
import numpy as np
import sys
from pathlib import Path
import threading


# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from mainflow.audio import AudioStream
from mainflow.vad import VAD
from mainflow.audio2text import Transcriber
from mainflow.text2audio import Synthesizer
from utils.session import Session
from utils.logger import logger
from configs import settings

# Import from src.agents (note the src. prefix)
from src.agents import (
    generate_mom,
    reason_about_user,
)


class VoiceAssistant:
    def __init__(self):
        logger.info("Starting Real Estate Voice Assistant...")
        self.audio = AudioStream(rate=settings.SAMPLE_RATE, chunk=settings.CHUNK_SIZE) # creates microphone stream creates object of class
        self.vad = VAD(
            sample_rate=settings.SAMPLE_RATE,
            threshold=0.35,
            min_speech_duration_ms=250,
            min_silence_duration_ms=200,
            on_speech_end=self.on_speech_end
        )
        self.transcriber = Transcriber()
        self.synthesizer = Synthesizer()
        call_id = f"call_{int(time.time())}"
        self.session = Session(call_id)
        self.session.start_time = time.time()
        self.audio_buffer = bytearray() # stores raw speech bytes until call ends
        self.call_active = True
        self.last_activity_time = time.time()
        self.max_silence_seconds = 40
        self.reminder_sent = False
        self.ai_speaking = False
        self.ai_interrupted = False

    # triggered when silence is detected by VAD
    def on_speech_end(self):
        if len(self.audio_buffer) == 0:
            return
        
        # Transcribe
        logger.info("Processing speech...")
        audio_np = np.frombuffer(self.audio_buffer, dtype=np.int16).copy()
        self.audio_buffer.clear()
        
        try:
            user_text = self.transcriber.transcribe_array(audio_np)
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return
        self.last_activity_time = time.time()

        if not user_text: # empty
            return
        
        if len(user_text.strip()) <= 1:
            return
            
        try:
            logger.user(user_text)
            self.session.add_user_message(user_text)
            
            logger.info("🤖 Running reasoning agent...")
            recent_history = self.session.get_context_for_prompt(3)

            reasoning_output = reason_about_user(
                user_text=user_text,
                summary=self.session.summary + "\n" + recent_history,
                entities=self.session.entities,
            )

            intent = reasoning_output.get("intent", "unknown")
            entities = reasoning_output.get("entities", {})
            sentiment = reasoning_output.get("sentiment", "neutral")
            final_response = reasoning_output.get("final_response", "")
            lead_stage = reasoning_output.get("lead_stage", "new")
            end_call_flag = reasoning_output.get("end_call", False)
           

               
            self.session.business_state["lead_stage"] = lead_stage
            if lead_stage == "qualified":
                self.session.call_stage = "qualification"
            elif lead_stage == "hot":
                self.session.call_stage = "closing"
            elif end_call_flag:
                self.session.call_stage = "ended"
            # Speak response
            logger.ai(final_response)

            def speak_response():
                self.ai_speaking = True
                self.ai_interrupted = False
                self.synthesizer.synthesize_stream(final_response, self.audio.play_audio_chunk)
                self.ai_speaking = False

            threading.Thread(target=speak_response).start()
            # Save to session
            self.session.add_ai_message(final_response, {
                'intent': intent,
                'sentiment': sentiment,
                'entities': entities,
            })
            profile = f"""
            Customer Profile:
            - Name: {self.session.business_state.get('customer_name')}
            - Budget: {self.session.business_state.get('budget')}
            - Location: {self.session.business_state.get('location')}
            - Configuration: {self.session.business_state.get('configuration')}
            - Interested Properties: {self.session.insights.get('properties_discussed')}
            """

            call_state = f"""
            Call State:
            - Lead Stage: {lead_stage}
            - Last Intent: {intent}
            - Last Sentiment: {sentiment}
            - Objections Raised: {self.session.insights.get('objections')}
            """

            self.session.summary = profile + call_state
            # Respect supervisor lifecycle control
            if end_call_flag:
                self.end_call()
                return
        except Exception as e:
            logger.error(f"Agent failure: {e}")
            fallback_response = "I apologize, I am experiencing a temporary issue. Could you please repeat that?"
            self.synthesizer.synthesize_stream(fallback_response, self.audio.play_audio_chunk)

    def run(self):
        greeting = "Hello, thank you for calling our chakka real estate team. How may I assist you today?"
        def speak_greeting():
            self.ai_speaking = True
            self.ai_interrupted = False
            self.synthesizer.synthesize_stream(greeting, self.audio.play_audio_chunk)
            self.ai_speaking = False
            self.last_activity_time = time.time()

        threading.Thread(target=speak_greeting).start()
        self.session.add_ai_message(greeting, {
            "intent": "greeting",
            "sentiment": "neutral",
            "entities": {},
        })
        self.audio.start_input_stream()

        try:
            for chunk in self.audio.generate_chunks():
                silence_duration = time.time() - self.last_activity_time

                if (
                    silence_duration > 12
                    and not self.reminder_sent
                    and not self.ai_speaking
                ):
                    reminder = "Are you still there? Could you please respond?"

                    def speak_reminder():
                        self.ai_speaking = True
                        self.synthesizer.synthesize_stream(reminder, self.audio.play_audio_chunk)
                        self.ai_speaking = False

                    threading.Thread(target=speak_reminder).start()
                    self.reminder_sent = True

                if silence_duration > self.max_silence_seconds:
                    logger.system("Call ended due to inactivity")
                    self.end_call()
                    break
                if not self.call_active:
                    break
                speaking = self.vad.process_chunk(chunk)
                if speaking:
                    self.reminder_sent = False

                    if self.ai_speaking:
                        self.ai_interrupted = True
                        self.synthesizer.stop()
                    
                    self.last_activity_time = time.time()
                    self.audio_buffer.extend(chunk.tobytes())
        except KeyboardInterrupt:
            self.end_call()

    def end_call(self):
        if not self.call_active:
            return

        self.call_active = False
        logger.system("Call ended")
        farewell = "Thank you for contacting our chakka real estate team. Have a wonderful day."
        self.synthesizer.synthesize_stream(farewell, self.audio.play_audio_chunk)
        self.audio.close()
        self.session.business_state["call_status"] = "completed"
        try:
            transcript = self.session.get_full_transcript()

            mom_text = generate_mom(
                transcript=transcript,
                action_items=self.session.action_items,
                decisions=self.session.decisions,
                sentiment_timeline=self.session.sentiment_timeline,
                start_time=self.session.start_time,
                end_time=time.time(),
                business_state=self.session.business_state
            )

            self._save_mom(mom_text)
            self.session.save_to_file(f"mom/{self.session.call_id}_analytics.json")

        except Exception as e:
            logger.error(f"MoM generation failed: {e}")
    
    def _save_mom(self, mom_text):
        from pathlib import Path

        mom_dir = Path("mom")
        mom_dir.mkdir(exist_ok=True)

        filename = mom_dir / f"{self.session.call_id}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(mom_text)

        print("\n" + "=" * 60)
        print(mom_text)
        print("=" * 60)

        logger.info(f"📄 MoM saved to {filename}")

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()