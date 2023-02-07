import { useEffect, useRef, useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
// eslint-disable-next-line import/no-unresolved
import { PDFDocumentProxy } from 'pdfjs-dist/types/src/display/api'
import 'react-pdf/dist/esm/Page/TextLayer.css'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import { useForm } from 'react-hook-form'

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

const options = {
  cMapUrl: 'cmaps/',
  cMapPacked: true,
  standardFontDataUrl: 'standard_fonts/',
}

const App = () => {
  const [seminars, setSeminars] = useState<Seminar[]>([])
  const [allSeminarIds, setAllSeminarIds] = useState<string[]>([])

  // development時に２回useEffectが走ると、NASへのアクセスも連続して２回起き、その内の１つが失敗する。
  // そのため、development時においてもuseEffectは１回しか走らないようにする。
  const isFirstRender = useRef(true)
  useEffect(() => {
    if (isFirstRender.current && process.env.NODE_ENV === 'development') {
      isFirstRender.current = false
      return
    }
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

  const [currentDocument, setCurrentDocument] = useState<{ seminar: string; document: string } | null>(null)
  const [currentDocumentURL, setcurrentDocumentURL] = useState<string | null>(null)

  const handleOnClickDocument = (seminar: Seminar, document: string) => {
    if (currentDocument?.seminar === seminar.id && currentDocument?.document === document) return
    setCurrentDocument({ seminar: seminar.id, document })
  }

  useEffect(() => {
    if (!currentDocument) return
    const fetchDocumentData = async () => {
      const url = `/nas/${currentDocument.seminar}/${currentDocument.document}`
      const response = await fetch(url)
      const blob = await response.blob()
      const blobURL = URL.createObjectURL(blob)
      setcurrentDocumentURL(blobURL)
    }
    fetchDocumentData().catch(console.error)
  }, [currentDocument])

  const [numPages, setNumPages] = useState<number | null>(null)

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access,@typescript-eslint/restrict-template-expressions
    pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`
  }, [])

  function onDocumentLoadSuccess(pdf: PDFDocumentProxy) {
    setNumPages(pdf.numPages)
  }

  /*
   * 意図としては、seminarId に 新しい document (pdf) を追加するために
   * POSTリクエストを送っている。
   * 注意として、POSTリクエストのbodyに入っているデータ自体と、そのデータの解釈（サーバー上でどう扱うか。craeteするかupdateするか）
   * についてはfrontとbackで合意が必要。
   * */
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm()
  const onSubmit = async (data: any) => {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }
    console.log(data)
    const response = await fetch('/api/seminars/update', requestOptions)
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const jsonData = await response.json()
    console.log(jsonData)
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: '100px' }}>
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
      </div>
      <hr className="solid" />
      <h1>プレビュー</h1>
      {currentDocumentURL ? (
        <Document
          file={{ url: currentDocumentURL }}
          onLoadSuccess={(pdf) => onDocumentLoadSuccess(pdf)}
          options={options}
          renderMode="svg"
        >
          {Array.from(new Array(numPages), (el, index) => (
            <Page key={`page_${index + 1}`} pageNumber={index + 1} />
          ))}
        </Document>
      ) : null}
      <hr className="solid" />
      <h1>アップロード</h1>
      {/* eslint-disable-next-line @typescript-eslint/no-misused-promises */}
      <form action="/api/upload" method="post" encType="multipart/form-data" onSubmit={handleSubmit(onSubmit)}>
        {/* eslint-disable-next-line react/jsx-props-no-spreading */}
        <select {...register('seminar-id')}>
          {allSeminarIds.map((id) => (
            <option id="seminar id">{id}</option>
          ))}
        </select>
        {/* eslint-disable-next-line react/jsx-props-no-spreading */}
        <input type="file" {...register('file')} />
        <button type="submit">アップロード</button>
      </form>
    </div>
  )
}

export default App
