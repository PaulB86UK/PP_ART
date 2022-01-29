mod arc;
use arc::Args;
use image::ImageError;
use image::{io::Reader, ImageFormat, DynamicImage, ImageBuffer, GenericImageView, imageops::FilterType::Triangle};
use std::{io::BufReader, fs::File};
use std::convert::TryInto;

#[derive(Debug)]
enum ImageDataErrors {
    DifferentImageFormats,
    BuffertooSmall,
    UnableToReadImageFromPath(std::io::Error), //This one exists in the standard library
    UnableToFormatImage(String),
    UnableToDecodeImage(ImageError),
    UnableToSaveImage(ImageError)
}

struct FloatingImage {
    width: u32,
    height: u32,
    data: Vec<u8>,
    name: String,
}

impl FloatingImage {
    fn new(width: u32, height: u32, name: String) -> Self {
        let buffer_capacity = height * width * 4;
        let buffer = Vec::with_capacity(buffer_capacity.try_into().unwrap());
        FloatingImage {
            width,
            height,
            data: buffer,
            name,
        }
    }

    fn set_data(&mut self, data:Vec<u8>) -> Result<(),ImageDataErrors> {

        if data.len() > self.data.capacity() {
            //check if we can store
            return Err(ImageDataErrors::BuffertooSmall);
        }
        self.data = data;
        Ok(())
    }
}

fn main() -> Result<(),ImageDataErrors>{
    let args = Args::new();
    let (image_1,image_format_1) = find_image_from_path(args.image_1)?;  //Since we added the errors the ? propagates the error into the function, its the error propagation operator!!
    let (image_2,image_format_2) = find_image_from_path(args.image_2)?;
    if image_format_1 != image_format_2 {
        return  Err(ImageDataErrors::DifferentImageFormats);
    }
    let (image_1,image_2) = standarized_size(image_1, image_2);
    let mut output = FloatingImage::new(image_1.width(),image_1.height(), args.output);
    let combined_data = combine_image(image_1, image_2);
    output.set_data(combined_data)?; // check question functiionality "?" error propagation operator?
    if let Err(e) = image::save_buffer_with_format(output.name,&output.data, output.width, output.height, image::ColorType::Rgba8, image_format_1) {
        Err(ImageDataErrors::UnableToSaveImage(e))
    } else {
    Ok(())
    }
}

fn find_image_from_path(path: String) -> Result<(DynamicImage, ImageFormat), ImageDataErrors>{
    
    //let image_reader: Reader<BufReader<File>> = Reader::open(path).unwrap();
    //let image_format: ImageFormat = image_reader.format().unwrap();
    //let image: DynamicImage = image_reader.decode().unwrap();
    //The following is the translation of the above adding proper error handling.

    match Reader::open(&path) {
        Ok(image_reader) => {
        //2nd Line
            if let Some(image_format) = image_reader.format() {
                //3rd Line
                match image_reader.decode() {
                    Ok(image) => Ok((image, image_format)),
                    Err(e) => Err(ImageDataErrors::UnableToDecodeImage(e)) //e pass error as is;
                }

            } else {
                return Err(ImageDataErrors::UnableToFormatImage(path));
            }
        },
        Err(e) => Err(ImageDataErrors::UnableToReadImageFromPath(e))
        }
    }


fn get_smallest_dimension(dim_1: (u32,u32), dim_2: (u32,u32)) -> (u32,u32) {
    let pix_1 = dim_1.0 * dim_1.1;
    let pix_2 = dim_2.0 * dim_2.1;
    return if pix_1 < pix_2 {dim_1} else {dim_2};
}
fn standarized_size(image_1: DynamicImage, image_2: DynamicImage) -> (DynamicImage,DynamicImage) {
    let (width,height) =  get_smallest_dimension(image_1.dimensions(), image_2.dimensions());
    println!("width: {}, height: {}\n", width,height);

    if image_2.dimensions() == (width,height) {
        (image_1.resize_exact(width,height,Triangle), image_2)
    }
    else {
        (image_1, image_2.resize_exact(width
            , height, Triangle
        ))
    }
}

fn combine_image(image_1: DynamicImage, image_2: DynamicImage) -> Vec<u8> {
    let vec_1 = image_1.to_rgba8().into_vec();
    let vec_2 = image_2.to_rgba8().into_vec();

    alternate_pixels(vec_1,vec_2)

}

fn alternate_pixels(vec_1: Vec<u8>, vec_2: Vec<u8>) -> Vec<u8>{
    //if vec_1.len() == 5, then the vec macro create a vector like [0,0,0,0,0] (5)
    let mut combined_data = vec![0u8; vec_1.len()];
    //while loop to go on each pixel+
    /// need to declare i (this is not python)
    let mut i = 0; //obviusly its mut if not it wont change its value

    while i < vec_1.len() {
        if i % 8 == 0 {
            combined_data.splice(i..= i +3,set_rgba(&vec_1,i,i+3));  //i..= i +3 this means from i to i + 3
            }
        else {
            combined_data.splice(i..=i+3,set_rgba(&vec_2,i,i+3)); //not fully understand why this time is else since i=9 will replace preivous points?
        }
        i += 4; //increase by 4 because we are using rgb (3+1) 
    }
    combined_data
}
fn set_rgba(vec:&Vec<u8>, start: usize, end: usize) -> Vec<u8> {
    let mut rgba = Vec::new();
    for i in start..=end {
        let val = match vec.get(i) {
            Some(d) => *d,
            None => panic!("Index out of bounds"), 
        };
        rgba.push(val);
        }
    rgba
    
} 