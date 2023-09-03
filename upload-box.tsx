"use client";

import { CircularProgress, CircularProgressLabel } from "@chakra-ui/react";
import Image from "next/image";
import React, { useState, useRef, SetStateAction } from "react";
import { FaCloudUploadAlt } from "react-icons/fa";
import PitchDeckImage from "@/public/pitch-deck.png";
import { useUploadFile } from "@/services/hooks";

const UploadBox = ({
    setShowCamera,
}: {
    setShowCamera: React.Dispatch<SetStateAction<boolean>>;
}) => {
    const [file, setFile] = useState<File | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { uploadFile, uploadProgress, isSuccess } = useUploadFile("http://127.0.0.1:5000/upload");

    // console.log("File:", file);

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();

        const files = e.dataTransfer.files;

        if (files.length > 0) {
            setFile(files[0]);
            handleUpload(files[0]);
        }
    };

    const handleUpload = async (selectedFile: File) => {
        const formData = new FormData();
        formData.append("files", selectedFile);

        // const response = await fetch('http://127.0.0.1:5000/upload', {
        //     method: 'POST',
        //     body: formData,
        //   });

        uploadFile(formData);
    };

    const handleFileUpload = () => {
        if (file) {
            setFile(null);
        }
        fileInputRef.current?.click();
    };

    const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
            handleUpload(selectedFile);
        }
    };

    const handleCancel = () => {
        setFile(null);
    };

    const handleNext = () => {
        setShowCamera(true);
    };

    return (
        <div className="mt-12 flex flex-col">
            <div
                className={
                    "flex items-center py-10 sm:py-20 px-1 sm:px-8 justify-center flex-col gap-6 sm:gap-12 bg-[#7440E10D] border-2 border-dashed border-primary"
                }
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
            >
                {!file ? (
                    <>
                        <form className="sr-only">
                            <input
                                type="file"
                                id="myfile"
                                name="myfile"
                                accept=".pptx, .pdf, .doc, .docx"
                                ref={fileInputRef}
                                onChange={handleFileInputChange}
                            />
                        </form>
                        <button
                            className="bg-tertiary py-2 px-2 md:px-4 text-sm sm:text-lg rounded text-text-dark"
                            onClick={handleFileUpload}
                        >
                            <FaCloudUploadAlt className="inline-block mr-2 text-text-dark" />
                            Upload Your Slide File Here
                        </button>
                        <p className="font-body">Or Drag and Drop here</p>
                    </>
                ) : (
                    <div className="flex items-center flex-col md:flex-row justify-between gap-12 w-full lg:w-3/4">
                        {uploadProgress >= 100 && isSuccess ? (
                            <Image src={PitchDeckImage} alt="Pitch Deck" priority width={300} />
                        ) : (
                            <CircularProgress
                                value={uploadProgress}
                                color="brand.tertiary"
                                thickness="16px"
                                size="8rem"
                                trackColor="#AAAA55"
                                bg="white"
                                borderRadius="full"
                            >
                                <CircularProgressLabel color="bg.dark">
                                    {isNaN(uploadProgress) || !uploadProgress ? 0 : uploadProgress}%
                                </CircularProgressLabel>
                            </CircularProgress>
                        )}
                        <div className="flex flex-col gap-4 items-center md:items-start text-center md:text-left">
                            <h3
                                className={`${
                                    uploadProgress >= 100 ? "text-white" : "text-bg-ash"
                                }`}
                            >
                                {file.name}
                            </h3>
                            <p
                                className={`font-body text-sm sm:text-md ${
                                    uploadProgress >= 100 ? "text-bg-ash" : "text-white"
                                }`}
                            >
                                Transforming Dreams into presentations...
                            </p>
                        </div>
                    </div>
                )}
            </div>
            {file && (
                <div className="flex items-center gap-6 my-6 mx-auto flex-col sm:flex-row">
                    <button
                        className="py-2 text-sm sm:text-lg rounded text-white border-2 border-bg-light w-24 order-1 sm:order-0"
                        onClick={handleCancel}
                    >
                        Cancel
                    </button>
                    <button
                        className="bg-tertiary py-2 text-sm sm:text-lg rounded text-text-dark w-24 order-0 sm:order-1"
                        onClick={handleNext}
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
};

export default UploadBox;
