import React, { useState } from 'react';
import { Sliders, Wand2, MonitorPlay, Loader2, Zap } from 'lucide-react';

// Main Application Component
const App = () => {
  const [videoFile, setVideoFile] = useState(null);
  const [title, setTitle] = useState('');
  const [genre, setGenre] = useState('drama');
  const [model, setModel] = useState('hybrid');
  const [variants, setVariants] = useState(20);
  const [thumbnails, setThumbnails] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('video/')) {
      setVideoFile(file);
      setErrorMessage('');
    } else {
      setVideoFile(null);
      setErrorMessage('Please upload a valid video file.');
    }
  };



  const handleDownload = async (thumbnail, filename) => {
    try {
      // Use download URL if available, otherwise use image URL
      const downloadUrl = thumbnail.download_url || thumbnail.url;

      const response = await fetch(downloadUrl);
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || `thumbnail_${thumbnail.id}.jpg`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setSuccessMessage(`Downloaded: ${filename || `thumbnail_${thumbnail.id}.jpg`}`);
    } catch (error) {
      console.error('Download error:', error);
      setErrorMessage(`Download failed: ${error.message}`);
    }
  };

  const handleGenerate = async () => {
    if (!videoFile) {
      setErrorMessage('Please upload a video before generating.');
      return;
    }

    setErrorMessage('');
    setSuccessMessage('');
    setIsLoading(true);
    setThumbnails([]);

    try {
      const formData = new FormData();
      formData.append('video', videoFile);
      formData.append('title', title || 'Video Title');
      formData.append('genre', genre);
      formData.append('model', model);
      formData.append('variants', variants.toString());

      // Use direct backend URL to avoid Vercel proxy timeouts
      const response = await fetch('https://mehotter-thumbnail-forge-backend.hf.space/api/generate', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const data = await response.json();

      console.log('Response data:', data); // Debug log

      if (data.success) {
        console.log('Thumbnails received:', data.thumbnails); // Debug log

        if (!data.thumbnails || data.thumbnails.length === 0) {
          throw new Error('No thumbnails returned from server');
        }

        // Use the URLs provided by backend; ensure absolute as a safety
        const thumbnailsWithUrls = (data.thumbnails || []).map(thumb => {
          let url = thumb.url;
          if (typeof url === 'string' && !url.startsWith('http')) {
            url = `${url.startsWith('/') ? url : '/' + url}`;
          }
          const download_url = thumb.download_url && thumb.download_url.startsWith('http')
            ? thumb.download_url
            : url;

          return {
            ...thumb,
            url,
            download_url
          };
        });

        console.log('Processed thumbnails:', thumbnailsWithUrls.length);
        setThumbnails(thumbnailsWithUrls);
        setSuccessMessage(`Successfully generated ${data.thumbnails.length} thumbnails!`);
      } else {
        console.error('Server returned error:', data);
        throw new Error(data.error || 'Generation failed');
      }
    } catch (error) {
      setErrorMessage(`Error: ${error.message}`);
      console.error('Generation error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const InputCard = ({ icon: Icon, title, description, children }) => (
    <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700/50">
      <div className="flex items-start space-x-4 mb-4">
        <Icon className="w-6 h-6 text-indigo-400 mt-1 flex-shrink-0" />
        <div>
          <h2 className="text-xl font-bold text-white">{title}</h2>
          <p className="text-sm text-gray-400">{description}</p>
        </div>
      </div>
      {children}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 font-sans text-white p-4 sm:p-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-extrabold text-indigo-400 flex items-center justify-center space-x-3">
          <Wand2 className="w-8 h-8 md:w-10 md:h-10" />
          <span>AI Thumbnail Forge</span>
        </h1>
        <p className="text-gray-400 mt-2 text-lg">Generate high-converting video thumbnails using Netflix, Disney+, and Hybrid AI models.</p>
      </header>

      <main className="max-w-7xl mx-auto">
        {/* INPUT AND CONFIGURATION SECTION */}
        <section className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">

          {/* 1. Video Upload */}
          <InputCard icon={MonitorPlay} title="1. Upload Video" description="Select the video file you want to generate thumbnails for.">
            <label className="block">
              <span className="sr-only">Choose video file</span>
              <input
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-indigo-50 file:text-indigo-700
                  hover:file:bg-indigo-100
                  cursor-pointer
                  mt-3"
              />
            </label>
            <p className={`text-sm mt-3 ${videoFile ? 'text-green-400' : 'text-gray-500'}`}>
              {videoFile ? `File Selected: ${videoFile.name} (${(videoFile.size / 1024 / 1024).toFixed(2)} MB)` : 'No video selected.'}
            </p>
          </InputCard>

          {/* 2. Title & Genre */}
          <InputCard icon={Sliders} title="2. Video Details" description="Enter title and select genre for better results.">
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Video Title (e.g., Gujarati Drama Series)"
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:ring-indigo-500 focus:border-indigo-500 mb-3"
            />
            <select
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
              className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="drama">Drama</option>
              <option value="family">Family</option>
              <option value="action">Action</option>
              <option value="romance">Romance</option>
              <option value="thriller">Thriller</option>
              <option value="adventure">Adventure</option>
            </select>
          </InputCard>

          {/* 3. Model Selection */}
          <InputCard icon={Zap} title="3. Select AI Model" description="Choose the AI model for thumbnail generation.">
            <div className="space-y-3">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="model"
                  value="hybrid"
                  checked={model === 'hybrid'}
                  onChange={() => setModel('hybrid')}
                  className="form-radio h-4 w-4 text-indigo-500 bg-gray-700 border-gray-600 focus:ring-indigo-500"
                />
                <span className="text-white font-medium">Hybrid (Netflix + Disney+)</span>
              </label>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="model"
                  value="netflix"
                  checked={model === 'netflix'}
                  onChange={() => setModel('netflix')}
                  className="form-radio h-4 w-4 text-indigo-500 bg-gray-700 border-gray-600 focus:ring-indigo-500"
                />
                <span className="text-white font-medium">Netflix Model</span>
              </label>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="model"
                  value="disney"
                  checked={model === 'disney'}
                  onChange={() => setModel('disney')}
                  className="form-radio h-4 w-4 text-indigo-500 bg-gray-700 border-gray-600 focus:ring-indigo-500"
                />
                <span className="text-white font-medium">Disney+ Model</span>
              </label>
            </div>
            <div className="mt-4">
              <label className="block text-sm text-gray-400 mb-2">Number of Variants:</label>
              <input
                type="number"
                min="5"
                max="30"
                value={variants}
                onChange={(e) => setVariants(parseInt(e.target.value))}
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
              />
            </div>
          </InputCard>
        </section>

        {/* GENERATION BUTTON & STATUS */}
        <section className="text-center mb-12">
          <button
            onClick={handleGenerate}
            disabled={isLoading || !videoFile}
            className={`
              w-full sm:w-auto px-12 py-3 text-lg font-semibold rounded-full shadow-2xl transition duration-300 transform flex items-center justify-center mx-auto space-x-2
              ${isLoading
                ? 'bg-indigo-600 cursor-not-allowed opacity-70'
                : 'bg-indigo-500 hover:bg-indigo-600 hover:scale-105 active:scale-95'
              }
            `}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Wand2 className="w-5 h-5" />
                <span>Generate Thumbnails</span>
              </>
            )}
          </button>
          {errorMessage && (
            <p className="mt-4 text-red-400 font-medium">{errorMessage}</p>
          )}
          {successMessage && (
            <p className="mt-4 text-green-400 font-medium">{successMessage}</p>
          )}
        </section>

        {/* RESULTS SECTION — Thumbnails grid */}
        <section>
          <h2 className="text-3xl font-bold text-gray-200 mb-6 border-b border-gray-700 pb-2">
            Generated Thumbnails ({thumbnails.length})
          </h2>

          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            {thumbnails.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {thumbnails.map((thumb, index) => (
                  <div key={index} className="bg-gray-900 rounded-lg border border-gray-700 overflow-hidden">
                    <div className="aspect-[16/9] bg-gray-800">
                      <img
                        src={thumb.url}
                        alt={`Thumbnail ${index + 1}`}
                        className="w-full h-full object-cover"
                        loading="lazy"
                        onError={(e) => {
                          e.currentTarget.alt = 'Failed to load image';
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    </div>

                    <div className="p-4">
                      <p className="text-indigo-400 font-semibold mb-1">
                        Thumbnail #{index + 1}
                      </p>

                      {/* Optional metadata */}
                      <p className="text-gray-400 text-xs">
                        Scene: {thumb.scene_type || 'Unknown'} | Score: {thumb.score?.toFixed(2) || 'N/A'}
                      </p>

                      <p className="text-gray-500 text-xs break-all mt-1">{thumb.url}</p>

                      <div className="mt-3 flex flex-wrap gap-4">
                        <a
                          href={thumb.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-400 hover:text-blue-300 underline"
                        >
                          Open
                        </a>
                        <button
                          onClick={() => handleDownload(thumb, thumb.filename)}
                          className="text-sm text-green-400 hover:text-green-300 underline"
                        >
                          Download
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-400 py-12 border border-dashed border-gray-700 rounded-lg">
                {isLoading ? (
                  <div className="flex flex-col items-center justify-center text-indigo-400">
                    <Loader2 className="w-8 h-8 animate-spin mb-3" />
                    <p className="text-lg font-semibold">AI is working its magic...</p>
                    <p className="text-sm text-gray-400">Please wait while the models analyze your video.</p>
                  </div>
                ) : (
                  <p className="text-lg text-gray-400">Your generated thumbnails will appear here.</p>
                )}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default App;
