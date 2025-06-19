"""
AI Service Simulation for ZingyBooks
This module simulates the integration with ChatGPT 4o and Leonardo.ai APIs
"""

import random
import time
from datetime import datetime
from typing import Dict, List, Any

class ChatGPTService:
    """Simulates ChatGPT 4o API for story generation"""
    
    def __init__(self):
        self.api_key = None  # Will be set when real API key is provided
        
    def generate_story(self, child_name: str, child_age: int, birth_month: str, story_idea: str) -> Dict[str, Any]:
        """
        Simulate ChatGPT story generation
        In production, this would call the actual OpenAI API
        """
        # Simulate API processing time
        time.sleep(2)
        
        # Generate story title based on input
        story_themes = [
            "Magical Adventure", "Brave Quest", "Enchanted Journey", 
            "Secret Mission", "Wonderful Discovery", "Amazing Expedition"
        ]
        theme = random.choice(story_themes)
        title = f"{child_name}'s {theme}"
        
        # Generate story summary
        summary = f"Join {child_name} on an incredible {theme.lower()} filled with wonder, friendship, and discovery. This personalized story celebrates {child_name}'s unique spirit and imagination."
        
        # Generate detailed story pages
        pages = self._generate_story_pages(child_name, child_age, birth_month, story_idea, theme)
        
        return {
            "title": title,
            "summary": summary,
            "pages": pages,
            "generation_time": datetime.utcnow().isoformat(),
            "word_count": sum(len(page["content"].split()) for page in pages)
        }
    
    def _generate_story_pages(self, child_name: str, child_age: int, birth_month: str, story_idea: str, theme: str) -> List[Dict[str, Any]]:
        """Generate detailed story pages based on the theme and child information"""
        
        # Story templates based on different themes
        story_templates = {
            "Magical Adventure": self._magical_adventure_template,
            "Brave Quest": self._brave_quest_template,
            "Enchanted Journey": self._enchanted_journey_template,
            "Secret Mission": self._secret_mission_template,
            "Wonderful Discovery": self._wonderful_discovery_template,
            "Amazing Expedition": self._amazing_expedition_template
        }
        
        template_func = story_templates.get(theme, self._magical_adventure_template)
        return template_func(child_name, child_age, birth_month, story_idea)
    
    def _magical_adventure_template(self, child_name: str, child_age: int, birth_month: str, story_idea: str) -> List[Dict[str, Any]]:
        """Generate a magical adventure story"""
        return [
            {
                "page_number": 1,
                "title": "Front Cover",
                "content": f"{child_name}'s Magical Adventure\nA Personalized Story",
                "illustration_prompt": f"Book cover with {child_name} as a young hero in a magical setting, whimsical art style, bright colors"
            },
            {
                "page_number": 3,
                "title": "Chapter 1: The Ordinary Day",
                "content": f"It was a beautiful {birth_month} morning when {child_name}, who had just turned {child_age}, woke up feeling like something special was about to happen. Little did {child_name} know that this would be the most magical day of their life!",
                "illustration_prompt": f"{child_name} waking up in their bedroom, sunlight streaming through the window, excited expression"
            },
            {
                "page_number": 4,
                "title": "Chapter 2: The Mysterious Discovery",
                "content": f"While exploring the backyard, {child_name} noticed something glimmering behind the old oak tree. It was a shimmering portal that seemed to pulse with rainbow colors! {child_name}'s heart raced with excitement and curiosity.",
                "illustration_prompt": f"{child_name} discovering a magical glowing portal behind a large oak tree, rainbow colors, sense of wonder"
            },
            {
                "page_number": 5,
                "title": "Chapter 3: Stepping Into Magic",
                "content": f"With courage that surprised even {child_name}, they stepped through the portal and found themselves in the most beautiful magical land they had ever seen. Talking animals, floating islands, and crystal clear streams surrounded them.",
                "illustration_prompt": f"{child_name} stepping into a magical fantasy land with talking animals, floating islands, crystal streams"
            },
            {
                "page_number": 6,
                "title": "Chapter 4: Meeting New Friends",
                "content": f"A wise old owl named Oliver flew down to greet {child_name}. 'Welcome, brave one!' Oliver hooted. 'We've been waiting for someone with a pure heart like yours to help us solve a very important problem.'",
                "illustration_prompt": f"{child_name} meeting Oliver the wise owl, friendly conversation, magical forest background"
            },
            {
                "page_number": 7,
                "title": "Chapter 5: The Great Challenge",
                "content": f"Oliver explained that the magical land was slowly losing its colors because the Rainbow Crystal had been hidden away. Only someone brave and kind like {child_name} could find it and restore the land's beauty.",
                "illustration_prompt": f"Oliver the owl explaining the problem to {child_name}, showing a map, serious but hopeful mood"
            },
            {
                "page_number": 8,
                "title": "Chapter 6: The Journey Begins",
                "content": f"{child_name} didn't hesitate for a moment. 'I'll help!' they declared. With Oliver as their guide and a magical compass in hand, {child_name} set off on the greatest adventure of their life.",
                "illustration_prompt": f"{child_name} starting their quest with Oliver, holding a magical compass, determined expression"
            },
            {
                "page_number": 9,
                "title": "Chapter 7: The Enchanted Forest",
                "content": f"Their first stop was the Enchanted Forest, where {child_name} met a family of friendly rabbits who were sad because their home had lost its vibrant green color. {child_name} promised to help them too.",
                "illustration_prompt": f"{child_name} in an enchanted forest meeting sad rabbits, trees losing color, empathetic scene"
            },
            {
                "page_number": 10,
                "title": "Chapter 8: The Riddle of the Sphinx",
                "content": f"At the edge of the forest, a gentle sphinx posed a riddle to {child_name}: 'What grows stronger when shared and never runs out?' {child_name} thought carefully and answered, 'Kindness!' The sphinx smiled and let them pass.",
                "illustration_prompt": f"{child_name} solving a riddle with a friendly sphinx, thinking pose, magical atmosphere"
            },
            {
                "page_number": 11,
                "title": "Chapter 9: The Crystal Cave",
                "content": f"Following the compass, {child_name} discovered a beautiful crystal cave guarded by a lonely dragon. Instead of being scared, {child_name} approached with kindness and asked, 'Why are you so sad?'",
                "illustration_prompt": f"{child_name} approaching a sad dragon in a crystal cave, showing kindness instead of fear"
            },
            {
                "page_number": 12,
                "title": "Chapter 10: Understanding and Friendship",
                "content": f"The dragon explained that everyone was afraid of him, but he just wanted a friend. {child_name} sat down and listened to the dragon's stories, and soon they became the best of friends.",
                "illustration_prompt": f"{child_name} sitting with the dragon, sharing stories, friendship forming, warm atmosphere"
            },
            {
                "page_number": 13,
                "title": "Chapter 11: The Rainbow Crystal",
                "content": f"Grateful for {child_name}'s friendship, the dragon revealed that he had been protecting the Rainbow Crystal all along. 'You have shown me true kindness,' he said, 'and now I know you're the right person to use its power.'",
                "illustration_prompt": f"Dragon showing {child_name} the beautiful Rainbow Crystal, trust and friendship, magical glow"
            },
            {
                "page_number": 14,
                "title": "Chapter 12: Restoring the Magic",
                "content": f"With the Rainbow Crystal in hand, {child_name} watched in amazement as colors began flowing back into the magical land. The trees turned green, flowers bloomed in brilliant hues, and everyone cheered with joy!",
                "illustration_prompt": f"{child_name} holding the Rainbow Crystal as colors flow back into the land, magical restoration scene"
            },
            {
                "page_number": 15,
                "title": "Chapter 13: A Hero's Welcome",
                "content": f"All the creatures of the magical land gathered to celebrate {child_name}'s success. There was music, dancing, and a grand feast. {child_name} had never felt so proud and happy.",
                "illustration_prompt": f"Grand celebration with {child_name} as the hero, all magical creatures celebrating, festive atmosphere"
            },
            {
                "page_number": 16,
                "title": "Chapter 14: Lessons Learned",
                "content": f"As the celebration continued, {child_name} realized that the greatest magic wasn't in the crystal, but in the kindness they had shown and the friendships they had made along the way.",
                "illustration_prompt": f"{child_name} reflecting on their adventure, surrounded by new friends, wise and content expression"
            },
            {
                "page_number": 17,
                "title": "Chapter 15: The Gift of Friendship",
                "content": f"The dragon gave {child_name} a special scale that would always remind them of their friendship. Oliver presented them with a feather that would help them remember their courage.",
                "illustration_prompt": f"{child_name} receiving gifts from dragon and Oliver, meaningful exchange, emotional moment"
            },
            {
                "page_number": 18,
                "title": "Chapter 16: Time to Return",
                "content": f"As the sun began to set in the magical land, {child_name} knew it was time to return home. All their new friends gathered to say goodbye, promising that they would always be connected by the bonds of friendship.",
                "illustration_prompt": f"Emotional farewell scene with {child_name} and all their magical friends, sunset background"
            },
            {
                "page_number": 19,
                "title": "Chapter 17: The Journey Home",
                "content": f"Oliver guided {child_name} back to the portal. 'Remember,' the wise owl said, 'the magic you found here was inside you all along. You just needed to believe in yourself.'",
                "illustration_prompt": f"Oliver giving final wisdom to {child_name} at the portal, wise and encouraging scene"
            },
            {
                "page_number": 20,
                "title": "Chapter 18: Back to Reality",
                "content": f"{child_name} stepped back through the portal and found themselves in their own backyard again. But everything seemed different now – more colorful, more magical, more full of possibilities.",
                "illustration_prompt": f"{child_name} back in their backyard, but seeing it with new magical eyes, transformed perspective"
            },
            {
                "page_number": 21,
                "title": "Chapter 19: Sharing the Magic",
                "content": f"That evening, {child_name} shared their incredible adventure with their family. Even though some people might not believe in magic, {child_name} knew that kindness and courage were the most powerful magic of all.",
                "illustration_prompt": f"{child_name} telling their family about the adventure, warm family scene, storytelling moment"
            },
            {
                "page_number": 22,
                "title": "Chapter 20: The End of One Adventure",
                "content": f"As {child_name} drifted off to sleep that night, they smiled knowing that this was just the beginning. Tomorrow would bring new opportunities to be kind, brave, and magical in their own special way.",
                "illustration_prompt": f"{child_name} sleeping peacefully, dreaming of their adventure, content and happy"
            },
            {
                "page_number": 24,
                "title": "Back Cover",
                "content": f"The End of {child_name}'s Magical Adventure\n\nEvery child has magic within them. What adventure will you discover next?",
                "illustration_prompt": f"Back cover design with {child_name} and friends, inspiring message about inner magic"
            }
        ]
    
    def _brave_quest_template(self, child_name: str, child_age: int, birth_month: str, story_idea: str) -> List[Dict[str, Any]]:
        """Generate a brave quest story - simplified version for demo"""
        # This would be a full template like the magical adventure
        # For now, returning a shorter version
        return self._magical_adventure_template(child_name, child_age, birth_month, story_idea)
    
    def _enchanted_journey_template(self, child_name: str, child_age: int, birth_month: str, story_idea: str) -> List[Dict[str, Any]]:
        """Generate an enchanted journey story"""
        return self._magical_adventure_template(child_name, child_age, birth_month, story_idea)
    
    def _secret_mission_template(self, child_name: str, child_age: int, birth_month: str, story_idea: str) -> List[Dict[str, Any]]:
        """Generate a secret mission story"""
        return self._magical_adventure_template(child_name, child_age, birth_month, story_idea)
    
    def _wonderful_discovery_template(self, child_name: str, child_age: int, birth_month: str, story_idea: str) -> List[Dict[str, Any]]:
        """Generate a wonderful discovery story"""
        return self._magical_adventure_template(child_name, child_age, birth_month, story_idea)
    
    def _amazing_expedition_template(self, child_name: str, child_age: int, birth_month: str, story_idea: str) -> List[Dict[str, Any]]:
        """Generate an amazing expedition story"""
        return self._magical_adventure_template(child_name, child_age, birth_month, story_idea)


class LeonardoAIService:
    """Simulates Leonardo.ai API for illustration generation"""
    
    def __init__(self):
        self.api_key = None  # Will be set when real API key is provided
        
    def generate_illustration(self, prompt: str, child_name: str, page_number: int, story_id: int) -> Dict[str, Any]:
        """
        Simulate Leonardo.ai illustration generation
        In production, this would call the actual Leonardo.ai API
        """
        # Simulate API processing time
        time.sleep(3)
        
        # Generate two illustration options as specified
        illustrations = [
            {
                "url": f"/api/generated/leonardo/story_{story_id}_page_{page_number}_option_1.jpg",
                "style": "Concept Art",
                "model": "AlbedoBase XL",
                "dimensions": "1110x1110",
                "prompt_used": f"{prompt}, featuring {child_name}, whimsical children's book style, 1:1 aspect ratio"
            },
            {
                "url": f"/api/generated/leonardo/story_{story_id}_page_{page_number}_option_2.jpg", 
                "style": "Concept Art",
                "model": "AlbedoBase XL",
                "dimensions": "1110x1110",
                "prompt_used": f"{prompt}, featuring {child_name}, whimsical children's book style, 1:1 aspect ratio, alternative composition"
            }
        ]
        
        return {
            "illustrations": illustrations,
            "generation_time": datetime.utcnow().isoformat(),
            "page_number": page_number,
            "character_consistency": True,
            "face_integration": "Child's face successfully integrated"
        }
    
    def enhance_with_face_replacement(self, base_image_url: str, child_photo_url: str) -> str:
        """
        Simulate face replacement technology
        In production, this would use advanced AI face replacement
        """
        time.sleep(2)
        
        # Return enhanced image URL
        timestamp = int(datetime.utcnow().timestamp())
        return f"{base_image_url.replace('.jpg', f'_face_enhanced_{timestamp}.jpg')}"


# Service instances
chatgpt_service = ChatGPTService()
leonardo_service = LeonardoAIService()

