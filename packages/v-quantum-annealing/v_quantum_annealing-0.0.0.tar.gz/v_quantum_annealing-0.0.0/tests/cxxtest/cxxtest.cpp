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


// include Google Test
#include <gtest/gtest.h>
#include <gmock/gmock.h>

// include STL
#include <iostream>
#include <utility>
#include <numeric>
#include <random>
#include <tuple>
#include <type_traits>
#include <vector>
#include <algorithm>
#include <chrono>

// include v_quantum_annealing
#include <v_quantum_annealing/graph/all.hpp>
#include <v_quantum_annealing/system/all.hpp>
#include <v_quantum_annealing/updater/all.hpp>
#include <v_quantum_annealing/algorithm/all.hpp>
#include <v_quantum_annealing/result/all.hpp>
#include <v_quantum_annealing/utility/schedule_list.hpp>
#include <v_quantum_annealing/utility/union_find.hpp>
#include <v_quantum_annealing/utility/random.hpp>
#include <v_quantum_annealing/utility/gpu/memory.hpp>
#include <v_quantum_annealing/utility/gpu/cublas.hpp>
#include <v_quantum_annealing/sampler/sa_sampler.hpp>

// include Eigen
#include <Eigen/Dense>
#include <Eigen/Sparse>

// include tests
#define TEST_CASE_INDEX 1

#include "testcase.hpp"
#include "polynomial_test.hpp"

#include "sampler/all.hpp"
#include "system/all.hpp"
#include "graph/all.hpp"
#include "result/all.hpp"
#include "utility/all.hpp"

std::int32_t main(std::int32_t argc, char **argv) {
   testing::InitGoogleTest(&argc, argv);
   return RUN_ALL_TESTS();
}
