const { GoogleGenAI } = require('@google/genai');
const fs = require('fs');
const path = require('path');

const progressFile = path.join(__dirname, 'extraction_progress.json');
const partsDir = path.join(__dirname, 'data', 'parts');
const mappingPath = path.join(__dirname, 'data', 'parts_mapping.json');
const filteredPagesTextPath = path.join(__dirname, 'filtered_pages_summary.txt');
const finalJsonPath = path.join(__dirname, 'public', 'vocabulary.json');

// RPM limit for Gemini 3.1 Flash Lite is 15. We wait 5 seconds between requests.
const DELAY_MS = 5000;
const BATCH_SIZE = 10;

// Check API key
const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) {
  console.error('Error: GEMINI_API_KEY environment variable is not set.');
  console.error('Please run: $env:GEMINI_API_KEY="your_api_key_here" before running this script.');
  process.exit(1);
}

const ai = new GoogleGenAI({ apiKey });

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Check mapping
if (!fs.existsSync(mappingPath)) {
  console.error(`Error: ${mappingPath} not found. Please run split_pdf.cjs first.`);
  process.exit(1);
}
const mapping = JSON.parse(fs.readFileSync(mappingPath, 'utf8'));

// Parse filtered pages list
if (!fs.existsSync(filteredPagesTextPath)) {
  console.error(`Error: ${filteredPagesTextPath} not found. Please run filter_pages.cjs first.`);
  process.exit(1);
}

const lines = fs.readFileSync(filteredPagesTextPath, 'utf8').split('\n');
const pageNumbers = [];
for (const line of lines) {
  const match = line.match(/^Page\s+(\d+)\s+\(Index\s+\d+\)/);
  if (match) {
    pageNumbers.push(parseInt(match[1], 10));
  }
}

console.log(`Loaded ${pageNumbers.length} target page numbers from filtered list.`);
if (pageNumbers.length === 0) {
  console.error('No page numbers parsed. Check filtered_pages_summary.txt format.');
  process.exit(1);
}

// Define the strict JSON schema for output
const responseSchema = {
  type: 'ARRAY',
  description: 'A list of vocabulary words extracted from the specified page list of the PDF part.',
  items: {
    type: 'OBJECT',
    properties: {
      word: { type: 'STRING', description: 'The English vocabulary word, e.g. "atypical"' },
      phonetic: { type: 'STRING', description: 'The KK phonetic spelling, e.g. "[e`tipikl]" or "[əˈtɪpɪkl]", extracted visually' },
      structure: { type: 'STRING', description: 'Root/affix structure breakdown, separated by spaces and slashes, e.g. "a / typ / ical"' },
      literal_meaning: { type: 'STRING', description: 'Literal meaning of roots/affixes, separated by spaces and slashes, e.g. "without / type / 形容詞字尾"' },
      definition: { type: 'STRING', description: 'Traditional Chinese definition with part of speech inside brackets, e.g. "[形] 非典型的", "[名/動] 萎縮"' },
      synonyms: {
        type: 'ARRAY',
        items: { type: 'STRING' },
        description: 'Synonyms if listed on the page'
      },
      derivatives: {
        type: 'ARRAY',
        items: {
          type: 'OBJECT',
          properties: {
            word: { type: 'STRING', description: 'Derivative word form' },
            meaning: { type: 'STRING', description: 'Derivative meaning with part of speech, e.g. "[名] 深淵", "[形] 典型的"' }
          },
          required: ['word', 'meaning']
        },
        description: 'Derivatives listed under the word'
      },
      examples: {
        type: 'ARRAY',
        items: {
          type: 'OBJECT',
          properties: {
            en: { type: 'STRING', description: 'English example sentence' },
            zh: { type: 'STRING', description: 'Traditional Chinese translation of the example sentence' }
          },
          required: ['en', 'zh']
        },
        description: 'Example sentences'
      },
      part_name: { type: 'STRING', description: 'The current Part name printed on the page, e.g. "Part 1 通用學術字彙：依字首分類"' },
      chapter_name: { type: 'STRING', description: 'The current Chapter name printed on the page, e.g. "表示「否定」的字首"' },
      original_page: { type: 'INTEGER', description: 'The page number printed on the page layout itself (1-based, e.g. 43)' }
    },
    required: ['word', 'phonetic', 'structure', 'literal_meaning', 'definition', 'synonyms', 'derivatives', 'examples', 'part_name', 'chapter_name', 'original_page']
  }
};

async function main() {
  let progress = {
    pdfType: 'parts',
    uploadedParts: {}, // part_file -> fileUri
    lastProcessedIndex: 0,
    words: []
  };

  // Load progress if exists
  if (fs.existsSync(progressFile)) {
    try {
      const saved = JSON.parse(fs.readFileSync(progressFile, 'utf8'));
      if (saved.pdfType === 'parts') {
        progress = saved;
        console.log(`Resuming PDF parts extraction from page index ${progress.lastProcessedIndex}. Extracted words count so far: ${progress.words.length}`);
      } else {
        console.log('Found old/incompatible progress file, starting fresh.');
      }
    } catch (e) {
      console.log('Failed to parse progress file, starting fresh.');
    }
  }

  // Pre-map page list with their part files and local indices
  const pageTasks = pageNumbers.map((pNum) => {
    const mapped = mapping[pNum];
    if (!mapped) {
      console.error(`Error: Page ${pNum} has no mapping in parts_mapping.json`);
      process.exit(1);
    }
    return {
      originalPage: pNum,
      partFile: mapped.part_file,
      localPage: mapped.local_page
    };
  });

  const totalPagesCount = pageTasks.length;

  while (progress.lastProcessedIndex < totalPagesCount) {
    const startIndex = progress.lastProcessedIndex;
    
    // Group batch: limit batch size but also DO NOT cross part file boundary
    const firstTask = pageTasks[startIndex];
    const currentPartFile = firstTask.partFile;
    
    let endIndex = startIndex;
    while (
      endIndex < totalPagesCount && 
      (endIndex - startIndex) < BATCH_SIZE && 
      pageTasks[endIndex].partFile === currentPartFile
    ) {
      endIndex++;
    }

    const batchTasks = pageTasks.slice(startIndex, endIndex);
    const targetLocalPages = batchTasks.map(t => t.localPage);
    const targetOriginalPages = batchTasks.map(t => t.originalPage);

    console.log(`\n--- Batch: PDF Part File ${currentPartFile} ---`);
    console.log(`Local Pages inside part: ${targetLocalPages.join(', ')}`);
    console.log(`Original book pages: ${targetOriginalPages.join(', ')}`);
    console.log(`Progress index: ${startIndex + 1} to ${endIndex} of ${totalPagesCount}`);

    // Ensure the part file is uploaded
    if (!progress.uploadedParts[currentPartFile]) {
      const localPartPath = path.join(partsDir, currentPartFile);
      console.log(`Uploading ${localPartPath} to Gemini Files API...`);
      const file = await ai.files.upload({
        file: localPartPath,
        config: {
          mimeType: 'application/pdf',
          displayName: `Vocabulary ${currentPartFile}`
        }
      });
      console.log(`Uploaded successfully. File name: ${file.name}`);
      
      progress.uploadedParts[currentPartFile] = file.uri;
      fs.writeFileSync(progressFile, JSON.stringify(progress, null, 2), 'utf8');

      // Poll until file is ACTIVE
      let fileState = file.state;
      while (fileState === 'PROCESSING') {
        console.log('File is processing, waiting 5 seconds...');
        await sleep(5000);
        const check = await ai.files.get({ name: file.name });
        fileState = check.state;
        console.log(`File state: ${fileState}`);
      }

      if (fileState !== 'ACTIVE') {
        console.error(`File upload failed. File state is: ${fileState}`);
        process.exit(1);
      }
      console.log('File is ready for processing.');
    }

    const fileRef = {
      fileData: {
        fileUri: progress.uploadedParts[currentPartFile],
        mimeType: 'application/pdf'
      }
    };

    let attempts = 0;
    let success = false;
    let batchWords = [];

    while (attempts < 3 && !success) {
      try {
        attempts++;
        const prompt = `Please act as a precise data extractor. From the uploaded PDF document, extract all vocabulary entries from the following page numbers of the PDF file: ${targetLocalPages.join(', ')}.
Note: page numbers in this prompt refer to the 1-based page indices of this uploaded PDF file itself.
For each vocabulary entry on these pages:
1. Read the word, phonetic spelling, structure breakdown, literal meaning, definition, synonyms, derivatives, and example sentences visually (ignore any text layer encoding errors, look at the visual layout).
2. For structure breakdown and literal meaning, preserve the slashes and spacing as printed (e.g., use "a / typ / ical" instead of "a I typ I ical", "without / type / 形容詞字尾" instead of "without I type I 形容詞字尾").
3. For the definition, include the part of speech inside square brackets at the beginning, e.g., "[形] 非典型的", "[名/動] 萎縮".
4. Translate any corrupted or simplified Chinese characters in the definition, derivatives, and examples to standard Traditional Chinese.
5. Identify the Part name (e.g. "Part 1 通用學術字彙：依字首分類") and Chapter name (e.g. "表示「否定」的字首") printed on the page.
6. Identify the original page number printed on the bottom visual layout of the page itself (the visual footer page number). If a page has no printed page number, estimate it based on neighboring pages, or output the page index.
7. If a page contains no vocabulary entries (e.g., it is a chapter cover page, index, or preface), do not extract any items for that page. It is perfectly fine to return an empty list if none of the requested pages contain vocabulary words.
Output must strictly match the defined JSON schema.`;

        const response = await ai.models.generateContent({
          model: 'gemini-3.1-flash-lite',
          contents: [fileRef, prompt],
          config: {
            responseMimeType: 'application/json',
            responseSchema: responseSchema
          }
        });

        const textResponse = response.text;
        batchWords = JSON.parse(textResponse);
        success = true;
        console.log(`Successfully extracted ${batchWords.length} words from this batch.`);
      } catch (err) {
        console.error(`Attempt ${attempts} failed:`, err.message || err);
        if (attempts < 3) {
          console.log('Waiting 15 seconds before retry...');
          await sleep(15000);
        } else {
          console.error('Max attempts reached for this batch. Script stopping to preserve progress.');
          process.exit(1);
        }
      }
    }

    if (success) {
      progress.words.push(...batchWords);
      progress.lastProcessedIndex = endIndex;
      // Save progress
      fs.writeFileSync(progressFile, JSON.stringify(progress, null, 2), 'utf8');
      console.log(`Progress saved. Total words extracted: ${progress.words.length}`);

      if (progress.lastProcessedIndex < totalPagesCount) {
        console.log(`Cooling down for ${DELAY_MS / 1000} seconds to respect API rate limits...`);
        await sleep(DELAY_MS);
      }
    }
  }

  // Final assembly
  console.log('\nAll pages processed! Assembling public/vocabulary.json...');
  
  // Load chapters definition
  const chaptersDefPath = path.join(__dirname, 'data', 'chapters_definition.json');
  let chaptersDef = null;
  if (fs.existsSync(chaptersDefPath)) {
    chaptersDef = JSON.parse(fs.readFileSync(chaptersDefPath, 'utf8'));
    console.log('Loaded chapters_definition.json for grouping.');
  }

  function getOfficialPartAndChapter(page) {
    if (!chaptersDef) return null;
    for (const [partKey, partVal] of Object.entries(chaptersDef)) {
      if (page >= partVal.page_range[0] && page <= partVal.page_range[1]) {
        for (const ch of partVal.chapters) {
          if (page >= ch.page_range[0] && page <= ch.page_range[1]) {
            return {
              part_name: partVal.part_name,
              chapter_name: ch.chapter_name
            };
          }
        }
      }
    }
    return null;
  }

  // 1. Sort all words by original page and word alphabetical order
  progress.words.sort((a, b) => {
    if (a.original_page !== b.original_page) {
      return a.original_page - b.original_page;
    }
    return a.word.localeCompare(b.word);
  });

  // 2. Group into part/chapter structure
  const partsMap = new Map();
  let wordCounter = 1;

  for (const w of progress.words) {
    // Generate w_XXXX sequential ID
    const wordId = `w_${String(wordCounter++).padStart(4, '0')}`;
    
    // Get official names from chapters_definition.json, fallback to extracted values if not matching
    const official = getOfficialPartAndChapter(w.original_page);
    const partName = official ? official.part_name : (w.part_name || 'Part Unknown');
    const chapterName = official ? official.chapter_name : (w.chapter_name || 'Chapter Unknown');

    if (!partsMap.has(partName)) {
      partsMap.set(partName, new Map());
    }
    const chaptersMap = partsMap.get(partName);
    if (!chaptersMap.has(chapterName)) {
      chaptersMap.set(chapterName, []);
    }
    
    chaptersMap.get(chapterName).push({
      id: wordId,
      word: w.word,
      phonetic: w.phonetic,
      structure: w.structure,
      literal_meaning: w.literal_meaning,
      definition: w.definition,
      synonyms: w.synonyms,
      derivatives: w.derivatives,
      examples: w.examples,
      page: w.original_page
    });
  }

  // 3. Convert Map to final array structure (sorting according to chapters_definition.json)
  const finalJson = [];
  let partCounter = 1;

  const partKeysOrdered = chaptersDef ? Object.keys(chaptersDef) : [];
  const partNamesOrdered = partKeysOrdered.map(k => chaptersDef[k].part_name);

  for (const partName of partNamesOrdered) {
    if (partsMap.has(partName)) {
      const chaptersMap = partsMap.get(partName);
      const chaptersArray = [];
      
      const partKey = partKeysOrdered.find(k => chaptersDef[k].part_name === partName);
      const chapterOrder = chaptersDef[partKey].chapters.map(c => c.chapter_name);
      
      for (const chName of chapterOrder) {
        if (chaptersMap.has(chName)) {
          chaptersArray.push({
            chapter_name: chName,
            words: chaptersMap.get(chName)
          });
          chaptersMap.delete(chName);
        }
      }
      
      for (const [chName, words] of chaptersMap.entries()) {
        chaptersArray.push({
          chapter_name: chName,
          words: words
        });
      }
      
      finalJson.push({
        part_id: partCounter++,
        part_name: partName,
        chapters: chaptersArray
      });
      
      partsMap.delete(partName);
    }
  }

  for (const [partName, chaptersMap] of partsMap.entries()) {
    const chaptersArray = [];
    for (const [chapterName, words] of chaptersMap.entries()) {
      chaptersArray.push({
        chapter_name: chapterName,
        words: words
      });
    }
    finalJson.push({
      part_id: partCounter++,
      part_name: partName,
      chapters: chaptersArray
    });
  }

  fs.writeFileSync(finalJsonPath, JSON.stringify(finalJson, null, 2), 'utf8');
  console.log(`\nDone! Successfully created new ${finalJsonPath}`);
  
  if (fs.existsSync(progressFile)) {
    fs.unlinkSync(progressFile);
  }
}

main().catch(err => {
  console.error('Fatal Error:', err);
  process.exit(1);
});
