"use client";

import Image from "next/image";
import React, { useState, useRef, useEffect } from "react";
import Slider from "react-slick";
// import { howItWorksData } from "@/utils/staticData";

const settings = {
    className: "center",
    centerMode: true,
    infinite: false,
    centerPadding: "0px",
    slidesToShow: 1,
    speed: 500,
    adaptiveHeight: true,
    fade: true,
    swipeToSlide: true,
    focusOnSelect: true,
    nextArrow: <></>,
    prevArrow: <></>,
    // lazyLoad: true,
    // beforeChange: (current, next) => this.setState({ activeSlide: next }),
    // afterChange: current => this.setState({ activeSlide2: current }),
};

interface HowItWorksPropsType {
    howItWorksRef: React.MutableRefObject<Slider | null>;
}

const HowItWorks = ({ howItWorksRef }: HowItWorksPropsType) => {
    const [nav1, setNav1] = useState<Slider | undefined>(undefined);
    const [nav2, setNav2] = useState<Slider | undefined>(undefined);

    const slider1 = useRef<Slider | null>(null);
    const slider2 = howItWorksRef;

    useEffect(() => {
        setNav1(slider1.current as unknown as Slider);
        setNav2(slider2.current as unknown as Slider);
    }, [slider2]);

    const howItWorksData = []; 
    
    for(let i = 1; i < 11; i++){
        let v = i.toString();
       let Src =  "http://127.0.0.1:5000/static/image_" + v + ".png";   //This specfiy the link to images . This for loops was created to dynamically accomodate any image size

         howItWorksData.push(
            {
           
                        id: 1,
                        imgSrc: Src,
                    }
         )
    }

    // const howItWorksData = [
        
    //     {
           
    //         id: 1,
    //         imgSrc: "http://127.0.0.1:5000/static/image_1.png",
    //     },
    //     {
    //         id: 2,
    //         imgSrc: "http://127.0.0.1:5000/static/image_2.png",
    //     },
    //     {
    //         id: 3,
    //         imgSrc: "http://127.0.0.1:5000/static/image_3.png",
    //     },
    //     {
    //         id: 4,
    //         imgSrc: "http://127.0.0.1:5000/static/image_4.png",
    //     },
    //     {
    //         id: 5,
    //         imgSrc: "http://127.0.0.1:5000/static/image_5.png",
    //     },
    //     {
    //         id: 6,
    //         imgSrc: "http://127.0.0.1:5000/static/image_6.png",
    //     },
    //     {
    //         id: 7,
    //         imgSrc: "http://127.0.0.1:5000/static/image_.png",
    //     },
    // ];

    return (
        <section className="text-white rounded-xl my-8 mx-auto w-[98%] bg-bg-black max-w-[70rem]">
            <div className="max-w-[66rem] mx-auto w-full">
                <Slider asNavFor={nav2} ref={slider1} {...settings}>
                    {howItWorksData?.map((item) => (
                        <div key={item.id} className="cursor-pointer px-4">
                            <Image
                                src={item.imgSrc}
                                alt={item.imgSrc + " image"}
                                width={800}
                                height={300}
                                className="rounded h-full w-full max-h-[25rem]"
                            />
                        </div>
                    ))}
                </Slider>
            </div>
            <div className="mt-8 max-w-[60rem] mx-auto w-full bg-[#191919] rounded-md border-2 border-primary py-4 px-10 backdrop-blur-xl">
                <Slider
                    asNavFor={nav1}
                    ref={slider2}
                    slidesToShow={3}
                    swipeToSlide={true}
                    focusOnSelect={true}
                >
                    {howItWorksData?.map((item) => (
                        <div key={item.id} className="cursor-pointer px-2">
                            <Image
                                src={item.imgSrc}
                                alt={item.imgSrc + " slide"}
                                width={300}
                                height={100}
                                className="rounded-sm h-full w-full max-h-[8rem] object-fill"
                            />
                        </div>
                    ))}
                </Slider>
            </div>
        </section>
    );
};

export default HowItWorks;
