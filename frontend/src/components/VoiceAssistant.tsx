import { useState, useEffect, useRef, useCallback } from 'react';
import './VoiceAssistant.css';

interface VoiceCommand {
    command: string;
    action: string;
    params?: Record<string, string>;
}

interface VoiceAssistantProps {
    onCommand?: (command: VoiceCommand) => void;
    onTranscript?: (text: string) => void;
    onAssessmentData?: (data: AssessmentData) => void;
}

interface AssessmentData {
    roofArea?: number;
    surfaceType?: string;
    address?: string;
    tankCapacity?: number;
}

type ListeningState = 'idle' | 'listening' | 'processing' | 'speaking';

// Voice command patterns
const COMMAND_PATTERNS = [
    { pattern: /roof (area|size) (is |of )?(\d+\.?\d*)\s*(sqm|square meters?|sq\.? ?m)/i, action: 'set_roof_area', paramName: 'area' },
    { pattern: /(\d+\.?\d*)\s*(sqm|square meters?)\s*(roof)?/i, action: 'set_roof_area', paramName: 'area' },
    { pattern: /(concrete|tile|metal|asbestos|rcc|flat)\s*(roof)?/i, action: 'set_surface', paramName: 'type' },
    { pattern: /tank (capacity|size) (is |of )?(\d+)\s*(liters?|l|kl|kiloliters?)?/i, action: 'set_tank', paramName: 'capacity' },
    { pattern: /(\d+)\s*(liter|l)\s*tank/i, action: 'set_tank', paramName: 'capacity' },
    { pattern: /start (new )?assessment/i, action: 'start_assessment' },
    { pattern: /calculate|estimate|predict/i, action: 'calculate' },
    { pattern: /help|what can you do/i, action: 'help' },
];

export default function VoiceAssistant({ onCommand, onTranscript, onAssessmentData }: VoiceAssistantProps) {
    const [state, setState] = useState<ListeningState>('idle');
    const [transcript, setTranscript] = useState('');
    const [response, setResponse] = useState('');
    const [isSupported, setIsSupported] = useState(true);
    const [assessmentData, setAssessmentData] = useState<AssessmentData>({});
    const recognitionRef = useRef<any>(null);
    const synthRef = useRef<SpeechSynthesis | null>(null);

    useEffect(() => {
        // Check for speech recognition support
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (!SpeechRecognition) {
            setIsSupported(false);
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-IN'; // Indian English

        recognition.onstart = () => setState('listening');
        recognition.onend = () => {
            if (state === 'listening') setState('idle');
        };

        recognition.onresult = (event: any) => {
            const current = event.resultIndex;
            const result = event.results[current];
            const text = result[0].transcript;

            setTranscript(text);
            onTranscript?.(text);

            if (result.isFinal) {
                processCommand(text);
            }
        };

        recognition.onerror = (event: any) => {
            console.error('Speech recognition error:', event.error);
            setState('idle');
        };

        recognitionRef.current = recognition;
        synthRef.current = window.speechSynthesis;

        return () => {
            recognition.abort();
        };
    }, []);

    const processCommand = useCallback((text: string) => {
        setState('processing');
        let matched = false;
        let responseText = '';

        for (const { pattern, action, paramName } of COMMAND_PATTERNS) {
            const match = text.match(pattern);
            if (match) {
                matched = true;
                const command: VoiceCommand = { command: text, action };

                switch (action) {
                    case 'set_roof_area': {
                        const areaMatch = text.match(/(\d+\.?\d*)/);
                        if (areaMatch) {
                            const area = parseFloat(areaMatch[1]);
                            setAssessmentData(prev => {
                                const next = { ...prev, roofArea: area };
                                onAssessmentData?.(next);
                                return next;
                            });
                            responseText = `Roof area set to ${area} square meters.`;
                            command.params = { area: area.toString() };
                        }
                        break;
                    }
                    case 'set_surface': {
                        const typeMatch = match[1].toLowerCase();
                        const surfaceMap: Record<string, string> = {
                            'concrete': 'Flat Concrete',
                            'rcc': 'Flat Concrete',
                            'flat': 'Flat Concrete',
                            'tile': 'Sloped Tile',
                            'metal': 'Metal Sheet',
                            'asbestos': 'Asbestos',
                        };
                        const surfaceType = surfaceMap[typeMatch] || typeMatch;
                        setAssessmentData(prev => {
                            const next = { ...prev, surfaceType };
                            onAssessmentData?.(next);
                            return next;
                        });
                        responseText = `Surface type set to ${surfaceType}.`;
                        command.params = { type: surfaceType };
                        break;
                    }
                    case 'set_tank': {
                        const capacityMatch = text.match(/(\d+)/);
                        if (capacityMatch) {
                            let capacity = parseInt(capacityMatch[1]);
                            if (text.toLowerCase().includes('kl') || text.toLowerCase().includes('kiloliter')) {
                                capacity *= 1000;
                            }
                            setAssessmentData(prev => {
                                const next = { ...prev, tankCapacity: capacity };
                                onAssessmentData?.(next);
                                return next;
                            });
                            responseText = `Tank capacity set to ${capacity} liters.`;
                            command.params = { capacity: capacity.toString() };
                        }
                        break;
                    }
                    case 'start_assessment':
                        setAssessmentData({});
                        responseText = "Starting new assessment. Tell me your roof area, surface type, and tank capacity.";
                        break;
                    case 'calculate':
                        if (assessmentData.roofArea) {
                            responseText = `Based on ${assessmentData.roofArea} square meters of ${assessmentData.surfaceType || 'roof'}, I estimate annual rainwater capture of approximately ${Math.round(assessmentData.roofArea * 1200 * 0.85 * 0.8)} liters.`;
                        } else {
                            responseText = "Please provide your roof area first.";
                        }
                        break;
                    case 'help':
                        responseText = "You can say things like: roof area is 100 square meters, concrete roof, tank capacity 5000 liters, or calculate.";
                        break;
                }

                onCommand?.(command);
                break;
            }
        }

        if (!matched) {
            responseText = "I didn't understand that. Try saying: roof area is 100 square meters.";
        }

        setResponse(responseText);
        speak(responseText);
    }, [assessmentData, onCommand, onAssessmentData]);

    const speak = (text: string) => {
        if (!synthRef.current) return;

        synthRef.current.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-IN';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        utterance.onstart = () => setState('speaking');
        utterance.onend = () => setState('idle');

        synthRef.current.speak(utterance);
    };

    const startListening = () => {
        if (recognitionRef.current && state === 'idle') {
            setTranscript('');
            recognitionRef.current.start();
        }
    };

    const stopListening = () => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            setState('idle');
        }
    };

    if (!isSupported) {
        return (
            <div className="voice-assistant voice-unsupported">
                <div className="voice-icon">🎙️</div>
                <p>Voice input not supported in this browser.</p>
            </div>
        );
    }

    return (
        <div className="voice-assistant">
            <div className="voice-header">
                <h3>🎙️ Voice Assistant</h3>
                <span className={`voice-status ${state}`}>{state}</span>
            </div>

            <div className="voice-visualization">
                <button
                    className={`voice-button ${state}`}
                    onMouseDown={startListening}
                    onMouseUp={stopListening}
                    onTouchStart={startListening}
                    onTouchEnd={stopListening}
                >
                    <div className="voice-rings">
                        <div className="ring ring-1"></div>
                        <div className="ring ring-2"></div>
                        <div className="ring ring-3"></div>
                    </div>
                    <span className="mic-icon">🎤</span>
                </button>
                <p className="voice-hint">
                    {state === 'idle' && 'Hold to speak'}
                    {state === 'listening' && 'Listening...'}
                    {state === 'processing' && 'Processing...'}
                    {state === 'speaking' && 'Speaking...'}
                </p>
            </div>

            {transcript && (
                <div className="voice-transcript">
                    <span className="label">You said:</span>
                    <p>{transcript}</p>
                </div>
            )}

            {response && (
                <div className="voice-response">
                    <span className="label">Assistant:</span>
                    <p>{response}</p>
                </div>
            )}

            {Object.keys(assessmentData).length > 0 && (
                <div className="voice-data">
                    <h4>Assessment Data</h4>
                    <ul>
                        {assessmentData.roofArea && <li>Roof Area: {assessmentData.roofArea} sqm</li>}
                        {assessmentData.surfaceType && <li>Surface: {assessmentData.surfaceType}</li>}
                        {assessmentData.tankCapacity && <li>Tank: {assessmentData.tankCapacity} L</li>}
                    </ul>
                </div>
            )}

            <div className="voice-commands">
                <h4>Try saying:</h4>
                <div className="command-chips">
                    <span>"Roof area is 120 square meters"</span>
                    <span>"Concrete roof"</span>
                    <span>"5000 liter tank"</span>
                    <span>"Calculate"</span>
                </div>
            </div>
        </div>
    );
}
