use super::RustBaseApiClass;
use crate::aug::character::OcrAugmentor;
use crate::aug::{AugCountParams, BaseAugmentor};
use crate::doc::Doc;
use crate::model::character::OcrModel;
use pyo3::prelude::*;
use rand::{rngs::StdRng, SeedableRng};
use std::collections::HashSet;
use std::sync::Arc;
use std::thread;

/// Api Class to perform OCR model augmentations on input
#[pyclass]
pub struct RustOCRApiClass {
    /// Parameteres to calculate number of chars that will be augmented in single word
    aug_char_params: AugCountParams,
    /// Parameteres to calculate number of words that will be augmented
    aug_word_params: AugCountParams,
    /// OcrModel
    model: Arc<OcrModel>,
    /// Filter, Set of words that cannot be augmented
    stopwords: Arc<Option<HashSet<String>>>,
    /// Filter, do not augment word, if it's lenght less than this value
    min_char: Option<usize>,
}

impl RustOCRApiClass {
    fn get_aug_char_params(&self) -> AugCountParams {
        self.aug_char_params.clone()
    }

    fn get_aug_word_params(&self) -> AugCountParams {
        self.aug_word_params.clone()
    }

    fn get_min_chars(&self) -> Option<usize> {
        self.min_char
    }
}

#[pymethods]
impl RustOCRApiClass {
    #[new]
    #[pyo3(signature = (
        aug_min_char, aug_max_char, aug_p_char,
        aug_min_word, aug_max_word, aug_p_word,
        stopwords, min_char, dict_of_path)
    )]
    fn new(
        aug_min_char: Option<usize>,
        aug_max_char: Option<usize>,
        aug_p_char: Option<f32>,
        aug_min_word: Option<usize>,
        aug_max_word: Option<usize>,
        aug_p_word: Option<f32>,
        stopwords: Option<HashSet<String>>,
        min_char: Option<usize>,
        dict_of_path: String,
    ) -> Self {
        let mut model = OcrModel::new(dict_of_path);
        model.load_model();
        RustOCRApiClass {
            aug_char_params: AugCountParams::new(aug_min_char, aug_max_char, aug_p_char),
            aug_word_params: AugCountParams::new(aug_min_word, aug_max_word, aug_p_word),
            model: Arc::new(model),
            stopwords: Arc::new(stopwords),
            min_char: min_char,
        }
    }

    fn augment_string_single_thread(&self, input_string: String, n: usize) -> Vec<String> {
        RustBaseApiClass::augment_string_single_thread(self, input_string, n)
    }

    fn augment_string_multi_thread(
        &self,
        input_string: String,
        n: usize,
        n_threads: usize,
    ) -> Vec<String> {
        RustBaseApiClass::augment_string_multi_thread(self, input_string, n, n_threads)
    }

    fn augment_list_single_thread(&self, input_list: Vec<String>) -> Vec<String> {
        RustBaseApiClass::augment_list_single_thread(self, input_list)
    }

    fn augment_list_multi_thread(&self, input_list: Vec<String>, n_threads: usize) -> Vec<String> {
        RustBaseApiClass::augment_list_multi_thread(self, input_list, n_threads)
    }
}

impl RustBaseApiClass<OcrAugmentor, OcrModel> for RustOCRApiClass {
    fn create_augmentor_instance(&self) -> OcrAugmentor {
        OcrAugmentor::new(
            self.get_aug_char_params(),
            self.get_aug_word_params(),
            self.get_min_chars(),
            Arc::clone(&self.model),
            Arc::clone(&self.stopwords),
        )
    }

    fn create_thread_handle_string(
        &self,
        input_string_ref: Arc<String>,
        n_on_thread: usize,
    ) -> thread::JoinHandle<Vec<String>> {
        let aug_params_char_cloned = self.get_aug_char_params();
        let aug_params_word_cloned = self.get_aug_word_params();
        let min_chars_cloned = self.get_min_chars();
        let arc_model_ref = Arc::clone(&self.model);
        let arc_stopword_ref = Arc::clone(&self.stopwords);

        let thread_handle = thread::spawn(move || {
            let mut rng: StdRng = SeedableRng::from_entropy();
            let mut thread_res = Vec::with_capacity(n_on_thread);
            let mut doc = Doc::from_arc(input_string_ref);
            let augmentor = OcrAugmentor::new(
                aug_params_char_cloned,
                aug_params_word_cloned,
                min_chars_cloned,
                arc_model_ref,
                arc_stopword_ref,
            );
            for _ in 0..n_on_thread {
                augmentor.augment(&mut doc, &mut rng);
                thread_res.push(doc.get_augmented_string());
                doc.set_to_original();
            }
            thread_res
        });
        thread_handle
    }

    fn create_thread_handle_list(
        &self,
        input_list_ref: Arc<Vec<String>>,
        left_idx: usize,
        right_idx: usize,
    ) -> thread::JoinHandle<Vec<String>> {
        let aug_params_char_cloned = self.get_aug_char_params();
        let aug_params_word_cloned = self.get_aug_word_params();
        let min_chars_cloned = self.get_min_chars();
        let arc_model_ref = Arc::clone(&self.model);
        let arc_stopword_ref = Arc::clone(&self.stopwords);

        let thread_handle = thread::spawn(move || {
            let mut rng: StdRng = SeedableRng::from_entropy();
            let mut thread_res = Vec::with_capacity(right_idx - left_idx);
            let augmentor = OcrAugmentor::new(
                aug_params_char_cloned,
                aug_params_word_cloned,
                min_chars_cloned,
                arc_model_ref,
                arc_stopword_ref,
            );

            for input in &input_list_ref.as_ref()[left_idx..right_idx] {
                let mut doc = Doc::new(input);
                augmentor.augment(&mut doc, &mut rng);
                thread_res.push(doc.get_augmented_string());
            }
            thread_res
        });
        thread_handle
    }
}
