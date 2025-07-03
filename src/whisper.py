from flask import request, jsonify
import openai
import os
import logging
import tempfile
import re
from typing import Dict, List, Any
import json
from .config import OPENAI_WHISPER_MODEL

logger = logging.getLogger(__name__)

# Mock franc-like language detection (in real implementation, you'd use a Python franc library)
def analyze_with_franc(text: str) -> Dict[str, Any]:
    """Analyze text language using character-based detection (franc-like)"""
    if not text or len(text) < 5:
        return {
            'primary': 'unknown',
            'languages': [],
            'confidence': 0,
            'alternatives': []
        }
    
    # Character analysis
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = len(re.sub(r'\s', '', text))  # Exclude spaces
    
    chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
    english_ratio = english_chars / total_chars if total_chars > 0 else 0
    
    logger.info(f'Language analysis: chinese={chinese_chars}, english={english_chars}, total={total_chars}')
    
    # Determine language distribution
    primary = 'unknown'
    languages = []
    confidence = 0
    
    if chinese_ratio > 0.1 and english_ratio > 0.1:
        # Mixed language
        primary = 'zh' if chinese_ratio >= english_ratio else 'en'
        languages = ['zh', 'en']
        confidence = 0.9
    elif chinese_ratio > 0.05:
        # Chinese dominant
        primary = 'zh'
        languages = ['zh']
        confidence = min(0.9, chinese_ratio * 2)
    elif english_ratio > 0.1:
        # English dominant
        primary = 'en'
        languages = ['en']
        confidence = min(0.9, english_ratio * 2)
    else:
        # Unknown/other
        primary = 'unknown'
        languages = []
        confidence = 0.3
    
    alternatives = []
    if chinese_ratio > 0:
        alternatives.append({'lang': 'zh', 'confidence': chinese_ratio})
    if english_ratio > 0:
        alternatives.append({'lang': 'en', 'confidence': english_ratio})
    
    return {
        'primary': primary,
        'languages': languages,
        'confidence': confidence,
        'alternatives': alternatives
    }

def transcribe_with_chinese_optimization(file_path: str) -> Dict[str, Any]:
    """Transcribe with Chinese optimization"""
    try:
        with open(file_path, 'rb') as audio_file:
            transcription = openai.audio.transcriptions.create(
                file=audio_file,
                model=OPENAI_WHISPER_MODEL,
                response_format='verbose_json',
                language='zh',
                prompt='这段录音可能包含中文和英文混合内容。请完整准确地转录所有语言，保持原始语言不要翻译。如果有英文单词或句子，请保留英文原文。Chinese and English mixed content, transcribe exactly as spoken, do not translate.',
                temperature=0
            )
        
        return {
            'text': transcription.text or '',
            'language': transcription.language or 'zh',
            'duration': transcription.duration or 0,
            'segments': transcription.segments or []
        }
    except Exception as e:
        logger.error(f'Chinese optimization transcription error: {e}')
        return {
            'text': '',
            'language': 'zh',
            'duration': 0,
            'segments': []
        }

def transcribe_auto_detect(file_path: str) -> Dict[str, Any]:
    """Transcribe with auto language detection"""
    try:
        with open(file_path, 'rb') as audio_file:
            transcription = openai.audio.transcriptions.create(
                file=audio_file,
                model=OPENAI_WHISPER_MODEL,
                response_format='verbose_json',
                temperature=0
            )
        
        return {
            'text': transcription.text or '',
            'language': transcription.language or 'unknown',
            'duration': transcription.duration or 0,
            'segments': transcription.segments or []
        }
    except Exception as e:
        logger.error(f'Auto detect transcription error: {e}')
        return {
            'text': '',
            'language': 'unknown',
            'duration': 0,
            'segments': []
        }

def select_best_result_english_first(results: Dict[str, Any]) -> Dict[str, Any]:
    """Select best transcription result with English-first strategy"""
    english_result = results.get('english', {})
    chinese_result = results.get('chinese', {})
    
    english_franc = english_result.get('franc', {})
    chinese_franc = chinese_result.get('franc', {})
    
    # If English is confident and no significant Chinese, use English
    if (english_franc.get('primary') == 'en' and 
        english_franc.get('confidence', 0) > 0.7 and
        not re.search(r'[\u4e00-\u9fff]', english_result.get('text', ''))):
        
        return {
            'text': english_result.get('text', ''),
            'detectedLanguages': english_franc.get('languages', []),
            'primaryLanguage': english_franc.get('primary', 'en'),
            'renderingLanguage': 'en',
            'confidence': {'auto_confident_english': english_franc.get('confidence', 0)},
            'strategy': 'auto_confident_english',
            'mixedLanguage': False,
            'francAnalysis': {
                'detected': english_franc.get('primary', 'en'),
                'confidence': english_franc.get('confidence', 0),
                'alternatives': english_franc.get('alternatives', [])
            }
        }
    
    # Otherwise, use the result with better confidence
    english_confidence = english_franc.get('confidence', 0)
    chinese_confidence = chinese_franc.get('confidence', 0)
    
    if english_confidence >= chinese_confidence:
        return {
            'text': english_result.get('text', ''),
            'detectedLanguages': english_franc.get('languages', []),
            'primaryLanguage': english_franc.get('primary', 'en'),
            'renderingLanguage': 'en',
            'confidence': {'english_preferred': english_confidence},
            'strategy': 'english_preferred',
            'mixedLanguage': len(english_franc.get('languages', [])) > 1,
            'francAnalysis': {
                'detected': english_franc.get('primary', 'en'),
                'confidence': english_confidence,
                'alternatives': english_franc.get('alternatives', [])
            }
        }
    else:
        return {
            'text': chinese_result.get('text', ''),
            'detectedLanguages': chinese_franc.get('languages', []),
            'primaryLanguage': chinese_franc.get('primary', 'zh'),
            'renderingLanguage': 'zh',
            'confidence': {'chinese_preferred': chinese_confidence},
            'strategy': 'chinese_preferred',
            'mixedLanguage': len(chinese_franc.get('languages', [])) > 1,
            'francAnalysis': {
                'detected': chinese_franc.get('primary', 'zh'),
                'confidence': chinese_confidence,
                'alternatives': chinese_franc.get('alternatives', [])
            }
        }

def enhanced_transcription(file_path: str) -> Dict[str, Any]:
    """Enhanced transcription with language detection"""
    logger.info('🔍 Starting detect-first transcription flow...')
    
    try:
        # 1. Auto language detection
        logger.info('🕵️‍♂️ Whisper auto-detect pass...')
        auto_result = transcribe_auto_detect(file_path)
        auto_franc = analyze_with_franc(auto_result['text'])
        
        logger.info(f'📊 Auto franc: {auto_franc}')
        
        has_chinese_chars = bool(re.search(r'[\u4e00-\u9fff]', auto_result['text']))
        
        # 2. If confident English and no Chinese characters, return directly
        if (auto_franc['primary'] == 'en' and 
            auto_franc['confidence'] > 0.7 and 
            not has_chinese_chars):
            
            logger.info('✅ Confident English detected, no Chinese fallback needed')
            return {
                'text': auto_result['text'],
                'detectedLanguages': auto_franc['languages'],
                'primaryLanguage': auto_franc['primary'],
                'renderingLanguage': 'en',
                'confidence': {'auto_confident_english': auto_franc['confidence']},
                'strategy': 'auto_confident_english',
                'mixedLanguage': False,
                'francAnalysis': {
                    'detected': auto_franc['primary'],
                    'confidence': auto_franc['confidence'],
                    'alternatives': auto_franc['alternatives']
                }
            }
        
        # 3. Run Chinese optimization as backup
        logger.info('🔄 Running Chinese-optimised pass for comparison...')
        chinese_result = transcribe_with_chinese_optimization(file_path)
        chinese_franc = analyze_with_franc(chinese_result['text'])
        
        # 4. Select best result
        final_result = select_best_result_english_first({
            'english': {**auto_result, 'franc': auto_franc},
            'chinese': {**chinese_result, 'franc': chinese_franc}
        })
        
        logger.info(f'✅ Final result: {final_result["strategy"]}, {final_result["renderingLanguage"]}')
        
        return final_result
        
    except Exception as error:
        logger.error(f'🟥 Detect-first transcription failed: {error}')
        
        # Fallback: simple auto mode
        fallback_franc = analyze_with_franc('')
        return {
            'text': '',
            'detectedLanguages': [],
            'primaryLanguage': 'unknown',
            'renderingLanguage': 'en',
            'confidence': {'detect_first_fallback': 0.3},
            'strategy': 'detect_first_fallback',
            'mixedLanguage': False,
            'francAnalysis': {
                'detected': 'unknown',
                'confidence': 0,
                'alternatives': []
            }
        }

def whisper_endpoint():
    """Handle audio transcription with enhanced language detection"""
    try:
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({'error': 'Missing audio file'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Log file details for debugging
        logger.info(f'📁 File details: name={file.filename}, type={file.content_type}, size={file.content_length}')
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
            
        try:
            # Use enhanced transcription
            logger.info('🚀 Using enhanced language detection...')
            enhanced_result = enhanced_transcription(temp_file_path)
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            # Return enhanced results
            logger.info(f'✅ Enhanced transcription completed: {enhanced_result["strategy"]}')
            
            return jsonify({
                'text': enhanced_result['text'],
                'language': enhanced_result['primaryLanguage'],
                'language_rendered': enhanced_result['renderingLanguage'],
                'duration': 0,  # Will be filled from transcription
                'segments': [],
                'enhanced': True,
                'debug': {
                    'fileSize': file.content_length,
                    'fileType': file.content_type,
                    'strategy': enhanced_result['strategy'],
                    'detectedLanguages': enhanced_result['detectedLanguages'],
                    'primaryLanguage': enhanced_result['primaryLanguage'],
                    'renderingLanguage': enhanced_result['renderingLanguage'],
                    'confidence': enhanced_result['confidence'],
                    'francAnalysis': enhanced_result['francAnalysis'],
                    'textAnalysis': {
                        'length': len(enhanced_result['text']),
                        'hasChinese': bool(re.search(r'[\u4e00-\u9fff]', enhanced_result['text'])),
                        'hasEnglish': bool(re.search(r'[a-zA-Z]', enhanced_result['text'])),
                        'isMixed': enhanced_result['mixedLanguage'],
                        'chineseRatio': next((alt['confidence'] for alt in enhanced_result['francAnalysis']['alternatives'] if alt['lang'] == 'zh'), 0),
                        'englishRatio': next((alt['confidence'] for alt in enhanced_result['francAnalysis']['alternatives'] if alt['lang'] == 'en'), 0)
                    }
                },
                'transcriptionDetails': {
                    'enhanced': enhanced_result,
                    'strategy': enhanced_result['strategy'],
                    'francDetected': enhanced_result['francAnalysis']['detected'],
                    'renderingLanguage': enhanced_result['renderingLanguage']
                }
            })
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
            
    except Exception as error:
        logger.error(f'🟥 Whisper API error: {error}')
        return jsonify({
            'error': 'Transcription failed',
            'details': str(error)
        }), 500 