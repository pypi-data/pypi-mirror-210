//    Copyright 2023 Jij Inc.

//    Licensed under the Apache License, Version 2.0 (the "License");
//    you may not use this file except in compliance with the License.
//    You may obtain a copy of the License at

//        http://www.apache.org/licenses/LICENSE-2.0

//    Unless required by applicable law or agreed to in writing, software
//    distributed under the License is distributed on an "AS IS" BASIS,
//    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//    See the License for the specific language governing permissions and
//    limitations under the License.

#include <pybind11/pybind11.h>
#include <pybind11/eval.h>
#include <pybind11_json/pybind11_json.hpp>

#include <type_traits>
// disable Eigen warning
#include <v_quantum_annealing/utility/disable_eigen_warning.hpp>
#include <v_quantum_annealing/utility/random.hpp>

#include "compile_config.hpp"
#include "declare.hpp"

PYBIND11_MODULE(cxxvqa, m) {
  py::options options;
  //options.disable_function_signatures();
  
  m.doc() = "v_quantum_annealing is a framework for ising and qubo";

  /**********************************************************
   //namespace graph
   **********************************************************/
  py::module m_graph = m.def_submodule("graph", "cxxvqa submodule for graph");

  v_quantum_annealing::declare_Graph(m_graph);

  v_quantum_annealing::declare_Dir(m_graph);
  v_quantum_annealing::declare_ChimeraDir(m_graph);

  // CPU version (v_quantum_annealing::FloatType)
  v_quantum_annealing::declare_Dense<v_quantum_annealing::FloatType>(m_graph, "");
  v_quantum_annealing::declare_Sparse<v_quantum_annealing::FloatType>(m_graph, "");
  v_quantum_annealing::declare_CSRSparse<v_quantum_annealing::FloatType>(m_graph, "");
  v_quantum_annealing::declare_Square<v_quantum_annealing::FloatType>(m_graph, "");
  v_quantum_annealing::declare_Chimera<v_quantum_annealing::FloatType>(m_graph, "");
  v_quantum_annealing::declare_Polynomial<v_quantum_annealing::FloatType>(m_graph, "");

  v_quantum_annealing::declare_BinaryPolynomialModel<v_quantum_annealing::FloatType>(m_graph);
  v_quantum_annealing::declare_IsingPolynomialModel<v_quantum_annealing::FloatType>(m_graph);

  py::module_ m_sampler = m.def_submodule("sampler");
  v_quantum_annealing::declare_SASampler<v_quantum_annealing::graph::BinaryPolynomialModel<v_quantum_annealing::FloatType>>(m_sampler, "BPM");
  v_quantum_annealing::declare_SASampler<v_quantum_annealing::graph::IsingPolynomialModel<v_quantum_annealing::FloatType>>(m_sampler, "IPM");

  // GPU version (v_quantum_annealing::GPUFloatType)
  if (!std::is_same<v_quantum_annealing::FloatType, v_quantum_annealing::GPUFloatType>::value) {
    v_quantum_annealing::declare_Dense<v_quantum_annealing::GPUFloatType>(m_graph, "GPU");
    v_quantum_annealing::declare_Sparse<v_quantum_annealing::GPUFloatType>(m_graph, "GPU");
    v_quantum_annealing::declare_CSRSparse<v_quantum_annealing::GPUFloatType>(m_graph, "GPU");
    v_quantum_annealing::declare_Square<v_quantum_annealing::GPUFloatType>(m_graph, "GPU");
    v_quantum_annealing::declare_Chimera<v_quantum_annealing::GPUFloatType>(m_graph, "GPU");
  } else {
    // raise warning
    std::cerr << "Warning: please use classes in Graph module without suffix "
                 "\"GPU\" or define type aliases."
              << std::endl;
  }

  /**********************************************************
   //namespace system
   **********************************************************/
  py::module m_system = m.def_submodule("system", "cxxvqa module for system");

  // ClassicalIsing
  v_quantum_annealing::declare_ClassicalIsing<v_quantum_annealing::graph::Dense<v_quantum_annealing::FloatType>>(
      m_system, "_Dense");
  v_quantum_annealing::declare_ClassicalIsing<v_quantum_annealing::graph::Sparse<v_quantum_annealing::FloatType>>(
      m_system, "_Sparse");
  v_quantum_annealing::declare_ClassicalIsing<v_quantum_annealing::graph::CSRSparse<v_quantum_annealing::FloatType>>(
      m_system, "_CSRSparse");
  v_quantum_annealing::declare_ClassicalIsingPolynomial<
      v_quantum_annealing::graph::Polynomial<v_quantum_annealing::FloatType>>(m_system, "_Polynomial");
  v_quantum_annealing::declare_KLocalPolynomial<
      v_quantum_annealing::graph::Polynomial<v_quantum_annealing::FloatType>>(m_system, "_Polynomial");

  // TransverselIsing
  v_quantum_annealing::declare_TransverseIsing<v_quantum_annealing::graph::Dense<v_quantum_annealing::FloatType>>(
      m_system, "_Dense");
  v_quantum_annealing::declare_TransverseIsing<v_quantum_annealing::graph::Sparse<v_quantum_annealing::FloatType>>(
      m_system, "_Sparse");
  v_quantum_annealing::declare_TransverseIsing<v_quantum_annealing::graph::CSRSparse<v_quantum_annealing::FloatType>>(
      m_system, "_CSRSparse");

  // Continuous Time Transeverse Ising
  v_quantum_annealing::declare_ContinuousTimeIsing<
      v_quantum_annealing::graph::Sparse<v_quantum_annealing::FloatType>>(m_system, "_Sparse");
  v_quantum_annealing::declare_ContinuousTimeIsing<
      v_quantum_annealing::graph::CSRSparse<v_quantum_annealing::FloatType>>(m_system, "_CSRSparse");

#ifdef USE_CUDA
  // ChimeraTransverseGPU
  v_quantum_annealing::declare_ChimeraTranseverseGPU<v_quantum_annealing::GPUFloatType,
                                         v_quantum_annealing::BLOCK_ROW, v_quantum_annealing::BLOCK_COL,
                                         v_quantum_annealing::BLOCK_TROT>(m_system);
  // ChimeraClassicalGPU
  v_quantum_annealing::declare_ChimeraClassicalGPU<v_quantum_annealing::GPUFloatType,
                                       v_quantum_annealing::BLOCK_ROW, v_quantum_annealing::BLOCK_COL>(
      m_system);
#endif

  /**********************************************************
   //namespace algorithm
   **********************************************************/
  py::module m_algorithm =
      m.def_submodule("algorithm", "cxxvqa module for algorithm");

  v_quantum_annealing::declare_UpdateMethod(m_algorithm);
  v_quantum_annealing::declare_RandomNumberEngine(m_algorithm);

  // singlespinflip
  v_quantum_annealing::declare_Algorithm_run<v_quantum_annealing::updater::SingleSpinFlip,
                                 v_quantum_annealing::system::ClassicalIsing<
                                     v_quantum_annealing::graph::Dense<v_quantum_annealing::FloatType>>,
                                 v_quantum_annealing::RandomEngine>(m_algorithm,
                                                        "SingleSpinFlip");
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::SingleSpinFlip,
      v_quantum_annealing::system::ClassicalIsing<
          v_quantum_annealing::graph::Sparse<v_quantum_annealing::FloatType>>,
      v_quantum_annealing::RandomEngine>(m_algorithm, "SingleSpinFlip");
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::SingleSpinFlip,
      v_quantum_annealing::system::ClassicalIsing<
          v_quantum_annealing::graph::CSRSparse<v_quantum_annealing::FloatType>>,
      v_quantum_annealing::RandomEngine>(m_algorithm, "SingleSpinFlip");
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::SingleSpinFlip,
      v_quantum_annealing::system::ClassicalIsingPolynomial<
          v_quantum_annealing::graph::Polynomial<v_quantum_annealing::FloatType>>,
      v_quantum_annealing::RandomEngine>(m_algorithm, "SingleSpinFlip");
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::KLocal,
      v_quantum_annealing::system::KLocalPolynomial<
          v_quantum_annealing::graph::Polynomial<v_quantum_annealing::FloatType>>,
      v_quantum_annealing::RandomEngine>(m_algorithm, "KLocal");
  v_quantum_annealing::declare_Algorithm_run<v_quantum_annealing::updater::SingleSpinFlip,
                                 v_quantum_annealing::system::TransverseIsing<
                                     v_quantum_annealing::graph::Dense<v_quantum_annealing::FloatType>>,
                                 v_quantum_annealing::RandomEngine>(m_algorithm,
                                                        "SingleSpinFlip");
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::SingleSpinFlip,
      v_quantum_annealing::system::TransverseIsing<
          v_quantum_annealing::graph::Sparse<v_quantum_annealing::FloatType>>,
      v_quantum_annealing::RandomEngine>(m_algorithm, "SingleSpinFlip");
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::SingleSpinFlip,
      v_quantum_annealing::system::TransverseIsing<
          v_quantum_annealing::graph::CSRSparse<v_quantum_annealing::FloatType>>,
      v_quantum_annealing::RandomEngine>(m_algorithm, "SingleSpinFlip");

  // swendsen-wang
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::SwendsenWang,
      v_quantum_annealing::system::ClassicalIsing<
          v_quantum_annealing::graph::Sparse<v_quantum_annealing::FloatType>>,
      v_quantum_annealing::RandomEngine>(m_algorithm, "SwendsenWang");
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::SwendsenWang,
      v_quantum_annealing::system::ClassicalIsing<
          v_quantum_annealing::graph::CSRSparse<v_quantum_annealing::FloatType>>,
      v_quantum_annealing::RandomEngine>(m_algorithm, "SwendsenWang");

  // Continuous time swendsen-wang
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::ContinuousTimeSwendsenWang,
      v_quantum_annealing::system::ContinuousTimeIsing<
          v_quantum_annealing::graph::Sparse<v_quantum_annealing::FloatType>>,
      v_quantum_annealing::RandomEngine>(m_algorithm, "ContinuousTimeSwendsenWang");
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::ContinuousTimeSwendsenWang,
      v_quantum_annealing::system::ContinuousTimeIsing<
          v_quantum_annealing::graph::CSRSparse<v_quantum_annealing::FloatType>>,
      v_quantum_annealing::RandomEngine>(m_algorithm, "ContinuousTimeSwendsenWang");

#ifdef USE_CUDA
  // GPU
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::GPU,
      v_quantum_annealing::system::ChimeraTransverseGPU<
          v_quantum_annealing::GPUFloatType, v_quantum_annealing::BLOCK_ROW, v_quantum_annealing::BLOCK_COL,
          v_quantum_annealing::BLOCK_TROT>,
      v_quantum_annealing::utility::cuda::CurandWrapper<v_quantum_annealing::GPUFloatType,
                                            v_quantum_annealing::GPURandomEngine>>(
      m_algorithm, "GPU");
  v_quantum_annealing::declare_Algorithm_run<
      v_quantum_annealing::updater::GPU,
      v_quantum_annealing::system::ChimeraClassicalGPU<
          v_quantum_annealing::GPUFloatType, v_quantum_annealing::BLOCK_ROW, v_quantum_annealing::BLOCK_COL>,
      v_quantum_annealing::utility::cuda::CurandWrapper<v_quantum_annealing::GPUFloatType,
                                            v_quantum_annealing::GPURandomEngine>>(
      m_algorithm, "GPU");
#endif

  /**********************************************************
   //namespace utlity
   **********************************************************/
  py::module m_utility =
      m.def_submodule("utility", "cxxvqa module for utility");

  v_quantum_annealing::declare_TemperatureSchedule(m_utility);

  // schedule_list
  v_quantum_annealing::declare_ClassicalUpdaterParameter(m_utility);
  v_quantum_annealing::declare_ClassicalConstraintUpdaterParameter(m_utility);
  v_quantum_annealing::declare_TransverseFieldUpdaterParameter(m_utility);

  v_quantum_annealing::declare_Schedule<v_quantum_annealing::system::classical_system>(m_utility,
                                                               "Classical");
  v_quantum_annealing::declare_Schedule<v_quantum_annealing::system::classical_constraint_system>(
      m_utility, "ClassicalConstraint");
  v_quantum_annealing::declare_Schedule<v_quantum_annealing::system::transverse_field_system>(
      m_utility, "TransverseField");

  m_utility.def("make_classical_schedule_list",
                &v_quantum_annealing::utility::make_classical_schedule_list, "beta_min"_a,
                "beta_max"_a, "one_mc_step"_a, "num_call_updater"_a);

  m_utility.def("make_classical_constraint_schedule_list",
                &v_quantum_annealing::utility::make_classical_constraint_schedule_list,
                "lambda"_a, "beta_min"_a, "beta_max"_a, "one_mc_step"_a,
                "num_call_updater"_a);

  m_utility.def("make_transverse_field_schedule_list",
                &v_quantum_annealing::utility::make_transverse_field_schedule_list,
                "beta"_a, "one_mc_step"_a, "num_call_updater"_a);

  /**********************************************************
   //namespace result
   **********************************************************/
  py::module m_result = m.def_submodule("result", "cxxvqa module for result");

  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::ClassicalIsing<
      v_quantum_annealing::graph::Dense<v_quantum_annealing::FloatType>>>(m_result);
  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::ClassicalIsing<
      v_quantum_annealing::graph::Sparse<v_quantum_annealing::FloatType>>>(m_result);
  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::ClassicalIsing<
      v_quantum_annealing::graph::CSRSparse<v_quantum_annealing::FloatType>>>(m_result);
  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::ClassicalIsingPolynomial<
      v_quantum_annealing::graph::Polynomial<v_quantum_annealing::FloatType>>>(m_result);
  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::KLocalPolynomial<
      v_quantum_annealing::graph::Polynomial<v_quantum_annealing::FloatType>>>(m_result);
  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::TransverseIsing<
      v_quantum_annealing::graph::Dense<v_quantum_annealing::FloatType>>>(m_result);
  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::TransverseIsing<
      v_quantum_annealing::graph::Sparse<v_quantum_annealing::FloatType>>>(m_result);
  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::TransverseIsing<
      v_quantum_annealing::graph::CSRSparse<v_quantum_annealing::FloatType>>>(m_result);
  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::ContinuousTimeIsing<
      v_quantum_annealing::graph::Sparse<v_quantum_annealing::FloatType>>>(m_result);
  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::ContinuousTimeIsing<
      v_quantum_annealing::graph::CSRSparse<v_quantum_annealing::FloatType>>>(m_result);
#ifdef USE_CUDA
  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::ChimeraTransverseGPU<
      v_quantum_annealing::GPUFloatType, v_quantum_annealing::BLOCK_ROW, v_quantum_annealing::BLOCK_COL,
      v_quantum_annealing::BLOCK_TROT>>(m_result);
  v_quantum_annealing::declare_get_solution<v_quantum_annealing::system::ChimeraClassicalGPU<
      v_quantum_annealing::GPUFloatType, v_quantum_annealing::BLOCK_ROW, v_quantum_annealing::BLOCK_COL>>(m_result);
#endif
}
