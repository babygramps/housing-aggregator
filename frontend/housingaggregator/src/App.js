import React, { useState } from 'react';
import styles from './App.module.css';
import neighborhoods from './neighborhoods'; // Assume neighborhoods is now an import

function App() {
  const [url, setUrl] = useState('');
  const [selectedNeighborhoods, setSelectedNeighborhoods] = useState([]);
  const [notionDbTitle, setNotionDbTitle] = useState('');
  const [error, setError] = useState('');

  const handleCheckboxChange = (value) => {
    setSelectedNeighborhoods(prevSelected => {
      if (prevSelected.includes(value)) {
        return prevSelected.filter(v => v !== value); // Uncheck the box
      } else {
        return [...prevSelected, value]; // Check the box
      }
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const payload = {
      url,
      params: { nh: selectedNeighborhoods },
      notion_db_title: notionDbTitle,
    };

    const endpoint = 'https://your-api-endpoint.com/path';

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        console.log('Data submitted successfully');
        const responseData = await response.json();
        console.log(responseData);
      } else {
        setError('Submission failed. Please try again.');
      }
    } catch (error) {
      setError(`Error: ${error.message}`);
    }
  };

  return (
    <div className={styles.container}>
       <h1 className={styles.title}>Craigslist Housing Aggregator</h1>
      <form onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label className={styles.label}>
            Craigslist URL:
            <input
              className={styles.input}
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </label>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Neighborhoods:</label>
          <div className={styles.checkboxContainer}>
            {neighborhoods.map(neighborhood => (
              <label key={neighborhood.value} className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  value={neighborhood.value}
                  onChange={() => handleCheckboxChange(neighborhood.value)}
                  checked={selectedNeighborhoods.includes(neighborhood.value)}
                />
                {neighborhood.name}
              </label>
            ))}
          </div>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>
            Notion Database Title:
            <input
              className={styles.input}
              type="text"
              value={notionDbTitle}
              onChange={(e) => setNotionDbTitle(e.target.value)}
            />
          </label>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <div className={styles.formGroup}>
          <button className={styles.button} type="submit">Submit</button>
        </div>
      </form>
    </div>
  );
}

export default App;
