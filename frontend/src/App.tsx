import React, { useEffect } from 'react'

type Seminar = {
  id: string
  title: string
  author: string
  date: string
  documents: string[]
}

type SeminarData = {
  '01': Seminar
  '02': Seminar
}

const App = () => {
  const [seminars, setSeminars] = React.useState<Seminar[]>([])
  const [allSeminarIds, setAllSeminarIds] = React.useState<string[]>([])

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch('/api/all')
      const data = await response.text()
      const seminarData = JSON.parse(data) as SeminarData
      setSeminars([
        { ...seminarData['01'], id: '01' },
        { ...seminarData['02'], id: '02' },
      ])
      setAllSeminarIds(['01', '02'])
    }
    fetchData().catch(console.error)
  }, [])

  const handleOnClickDocument = (seminar: Seminar, document: string) => {
    const fetchDocumentData = async () => {
      const response = await fetch(`/nas/${seminar.id}/${document}`)
      const data = await response.text()
      if (data !== currentDocument) setCurrentDocument(data)
    }
    fetchDocumentData().catch(console.error)
  }

  const [currentDocument, setCurrentDocument] = React.useState<string | null>(null)

  return (
    <div>
      {seminars.map((seminar) => (
        <div key={seminar.id}>
          <h1>{seminar.title}</h1>
          <h2>{seminar.author}</h2>
          <h3>{seminar.date}</h3>
          <ul>
            {seminar.documents.map((document) => (
              <li>
                {document}
                <button type="button" onClick={() => handleOnClickDocument(seminar, document)}>
                  open
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
      {currentDocument ? <div>{currentDocument}</div> : null}
    </div>
  )
}

export default App
