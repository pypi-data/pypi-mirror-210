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


TEST(PolyGraph, ConstructorCimodDenseInt) {
   TestPolyGraphConstructorCimodDense<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsDenseInt<double>());
}
TEST(PolyGraph, ConstructorCimodDenseString) {
   TestPolyGraphConstructorCimodDense<std::string, double>(GeneratePolynomialInteractionsDenseString<double>());
}
TEST(PolyGraph, ConstructorCimodDenseTuple2) {
   TestPolyGraphConstructorCimodDense<std::tuple<v_quantum_annealing::graph::Index, v_quantum_annealing::graph::Index>, double>(GeneratePolynomialInteractionsDenseTuple2<double>());
}
TEST(PolyGraph, ConstructorCimodSparseInt1) {
   TestPolyGraphConstructorCimodSparse<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt1<double>());
}
TEST(PolyGraph, ConstructorCimodSparseInt2) {
   TestPolyGraphConstructorCimodSparse<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt2<double>());
}
TEST(PolyGraph, ConstructorCimodSparseInt3) {
   TestPolyGraphConstructorCimodSparse<v_quantum_annealing::graph::Index, double>(GeneratePolynomialInteractionsSparseInt3<double>());
}

TEST(PolyGraph, AddInteractions1) {
   const v_quantum_annealing::graph::Index num_spins = 3;
   v_quantum_annealing::graph::Polynomial<double> poly_graph(num_spins);
   
   poly_graph.J(   {}    ) = +0.1  ;
   poly_graph.J(   {0}   ) = -0.5  ;
   poly_graph.J(   {1}   ) = +1.0  ;
   poly_graph.J(   {2}   ) = -2.0  ;
   poly_graph.J( {0, 1}  ) = +10.0 ;
   poly_graph.J( {0, 2}  ) = -20.0 ;
   poly_graph.J( {1, 2}  ) = +21.0 ;
   poly_graph.J({0, 1, 2}) = -120.0;
   
   TestPolyGraphDense(poly_graph);
}

TEST(PolyGraph, AddInteractions2) {
   const v_quantum_annealing::graph::Index num_spins = 3;
   v_quantum_annealing::graph::Polynomial<double> poly_graph(num_spins);
   
   poly_graph.J(       ) = +0.1  /2.0;
   poly_graph.J(   0   ) = -0.5  /2.0;
   poly_graph.J(   1   ) = +1.0  /2.0;
   poly_graph.J(   2   ) = -2.0  /2.0;
   poly_graph.J( 0, 1  ) = +10.0 /2.0;
   poly_graph.J( 0, 2  ) = -20.0 /2.0;
   poly_graph.J( 1, 2  ) = +21.0 /2.0;
   poly_graph.J(0, 1, 2) = -120.0/2.0;
   
   poly_graph.J(       ) += +0.1  /2.0;
   poly_graph.J(   0   ) += -0.5  /2.0;
   poly_graph.J(   1   ) += +1.0  /2.0;
   poly_graph.J(   2   ) += -2.0  /2.0;
   poly_graph.J( 0, 1  ) += +10.0 /2.0;
   poly_graph.J( 0, 2  ) += -20.0 /2.0;
   poly_graph.J( 1, 2  ) += +21.0 /2.0;
   poly_graph.J(0, 1, 2) += -120.0/2.0;
   
   TestPolyGraphDense(poly_graph);
}

TEST(PolyGraph, AddInteractions3) {
   const v_quantum_annealing::graph::Index num_spins = 3;
   v_quantum_annealing::graph::Polynomial<double> poly_graph(num_spins);
   
   poly_graph.J(       ) = +0.1  ;
   poly_graph.J(   0   ) = -0.5  ;
   poly_graph.J(   1   ) = +1.0  ;
   poly_graph.J(   2   ) = -2.0  ;
   poly_graph.J( 0, 1  ) = +10.0 ;
   poly_graph.J( 0, 2  ) = -20.0 ;
   poly_graph.J( 1, 2  ) = +21.0 ;
   poly_graph.J(0, 1, 2) = -120.0;
   
   TestPolyGraphDense(poly_graph);
}

TEST(PolyGraph, AddInteractions4) {
   const v_quantum_annealing::graph::Index num_spins = 3;
   v_quantum_annealing::graph::Polynomial<double> poly_graph(num_spins);
   
   poly_graph.J(       ) = +999999;
   poly_graph.J(   0   ) = +999999;
   poly_graph.J(   1   ) = +999999;
   poly_graph.J(   2   ) = +999999;
   poly_graph.J( 0, 1  ) = +999999;
   poly_graph.J( 0, 2  ) = +999999;
   poly_graph.J( 1, 2  ) = +999999;
   poly_graph.J(0, 1, 2) = +999999;
   
   poly_graph.J(       ) = +0.1  ;
   poly_graph.J(   0   ) = -0.5  ;
   poly_graph.J(   1   ) = +1.0  ;
   poly_graph.J(   2   ) = -2.0  ;
   poly_graph.J( 0, 1  ) = +10.0 ;
   poly_graph.J( 0, 2  ) = -20.0 ;
   poly_graph.J( 1, 2  ) = +21.0 ;
   poly_graph.J(0, 1, 2) = -120.0;
   
   TestPolyGraphDense(poly_graph);
}




}
}
