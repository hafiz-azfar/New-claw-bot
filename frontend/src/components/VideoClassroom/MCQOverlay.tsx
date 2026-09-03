import { useState } from 'react';

interface MCQQuestion {
  id: number;
  text: string;
  options: { id: number; text: string }[];
}

interface MCQOverlayProps {
  mcqData: {
    quiz_id: number;
    question: MCQQuestion;
    time_limit: number;
  };
  onClose: () => void;
}

export function MCQOverlay({ mcqData, onClose }: MCQOverlayProps) {
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [timeLeft, setTimeLeft] = useState(mcqData.time_limit || 30);

  // Countdown timer
  useState(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  });

  const handleSubmit = () => {
    if (selectedOption !== null) {
      // TODO: Submit answer to backend
      console.log('Submitting answer:', selectedOption);
      setSubmitted(true);
      
      // Auto-close after 2 seconds
      setTimeout(() => {
        onClose();
      }, 2000);
    }
  };

  return (
    <div className="mcq-overlay">
      <div className="mcq-card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">📝 Pop Quiz!</h2>
          <div className={`text-2xl font-bold ${timeLeft <= 10 ? 'text-red-500' : 'text-blue-400'}`}>
            ⏱ {timeLeft}s
          </div>
        </div>

        <p className="text-lg text-gray-200 mb-6">{mcqData.question.text}</p>

        <div className="space-y-3">
          {mcqData.question.options.map((option) => (
            <button
              key={option.id}
              onClick={() => !submitted && setSelectedOption(option.id)}
              className={`option-btn ${
                selectedOption === option.id ? 'selected' : ''
              } ${submitted ? 'opacity-50 cursor-not-allowed' : ''}`}
              disabled={submitted}
            >
              <span className="font-semibold mr-2">
                {String.fromCharCode(65 + option.id - 1)}.
              </span>
              {option.text}
            </button>
          ))}
        </div>

        {!submitted && (
          <div className="mt-6 flex gap-4">
            <button
              onClick={handleSubmit}
              disabled={selectedOption === null}
              className={`flex-1 btn-control ${
                selectedOption === null ? 'opacity-50 cursor-not-allowed' : 'btn-primary'
              }`}
            >
              Submit Answer
            </button>
            <button onClick={onClose} className="btn-control btn-secondary">
              Skip
            </button>
          </div>
        )}

        {submitted && (
          <div className="mt-6 text-center text-green-400 text-xl font-bold">
            ✅ Answer Submitted!
          </div>
        )}
      </div>
    </div>
  );
}
