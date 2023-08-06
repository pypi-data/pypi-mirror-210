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

#pragma once


namespace v_quantum_annealing {
namespace test {

TEST(PolySystemCIP, ConstructorCimodDenseInt) {
   TestCIPConstructorCimod<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsDenseInt<double>(), cimod::Vartype::SPIN, "Dense");
   TestCIPConstructorCimod<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsDenseInt<double>(), cimod::Vartype::BINARY, "Dense");
}
TEST(PolySystemCIP, ConstructorCimodDenseString) {
   TestCIPConstructorCimod<std::string, double>(GeneratePolynomialInteractionsDenseString<double>(), cimod::Vartype::SPIN, "Dense");
   TestCIPConstructorCimod<std::string, double>(GeneratePolynomialInteractionsDenseString<double>(), cimod::Vartype::BINARY, "Dense");
}
TEST(PolySystemCIP, ConstructorCimodDenseTuple2) {
   TestCIPConstructorCimod<std::tuple<v_quantum_annealing::graph::Index, v_quantum_annealing::graph::Index>, double>(GeneratePolynomialInteractionsDenseTuple2<double>(), cimod::Vartype::SPIN, "Dense");
   TestCIPConstructorCimod<std::tuple<v_quantum_annealing::graph::Index, v_quantum_annealing::graph::Index>, double>(GeneratePolynomialInteractionsDenseTuple2<double>(), cimod::Vartype::BINARY, "Dense");
}
TEST(PolySystemCIP, ConstructorCimodSparseInt1) {
   TestCIPConstructorCimod<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt1<double>(), cimod::Vartype::SPIN, "Sparse");
   TestCIPConstructorCimod<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt1<double>(), cimod::Vartype::BINARY, "Sparse");
}
TEST(PolySystemCIP, ConstructorCimodSparseInt2) {
   TestCIPConstructorCimod<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt2<double>(), cimod::Vartype::SPIN, "Sparse");
   TestCIPConstructorCimod<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt2<double>(), cimod::Vartype::BINARY, "Sparse");
}
TEST(PolySystemCIP, ConstructorCimodSparseInt3) {
   TestCIPConstructorCimod<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt3<double>(), cimod::Vartype::SPIN, "Sparse");
   TestCIPConstructorCimod<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt3<double>(), cimod::Vartype::BINARY, "Sparse");
}
TEST(PolySystemCIP, ConstructorGraphDenseInt) {
   TestCIPConstructorGraph<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsDenseInt<double>(), cimod::Vartype::SPIN, "Dense");
   TestCIPConstructorGraph<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsDenseInt<double>(), cimod::Vartype::BINARY, "Dense");
}
TEST(PolySystemCIP, ConstructorGraphSparseInt1) {
   TestCIPConstructorGraph<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt1<double>(), cimod::Vartype::SPIN, "Sparse");
   TestCIPConstructorGraph<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt1<double>(), cimod::Vartype::BINARY, "Sparse");
}
TEST(PolySystemCIP, ConstructorGraphSparseInt2) {
   TestCIPConstructorGraph<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt2<double>(), cimod::Vartype::SPIN, "Sparse");
   TestCIPConstructorGraph<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt2<double>(), cimod::Vartype::BINARY, "Sparse");
}



}
}
