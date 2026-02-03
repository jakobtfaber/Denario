"""MATLAB provider for mathematical computations."""

import time
from typing import List, Optional
import os
import json
import uuid
import shutil
import subprocess
from .base import MathematicalProvider, ComputationResult, ComputationError


class MATLABProvider(MathematicalProvider):
    """Provider using MATLAB R2024a for mathematical computations."""

    def __init__(
            self,
            matlab_path: Optional[str] = None,
            license_file: Optional[str] = None,
            backend: Optional[str] = None,
            container_name: Optional[str] = None,
            work_mount: Optional[str] = None,
            entrypoint: Optional[str] = None,
            **kwargs):
        super().__init__(
            capabilities=[
                'symbolic', 'numeric', 'visualization', 'optimization',
                'signal_processing', 'linear_algebra', 'statistics',
                'differential_equations', 'data_analysis'
            ],
            cost_per_query=0.0,  # Local license
            max_complexity='very_high',
            priority=1,
            **kwargs
        )
        self.matlab_path = matlab_path
        self.license_file = license_file
        # Docker backend configuration (optional)
        self.backend = backend or os.getenv("MATLAB_BACKEND")
        self.container_name = (
            container_name or os.getenv("MATLAB_DOCKER_CONTAINER")
        )
        self.work_mount = work_mount or os.getenv("MATLAB_WORK_MOUNT")
        self.entrypoint = entrypoint or os.getenv("MATLAB_ENTRYPOINT")

        self.engine = None
        # Initialize engine only if not using docker backend
        if self.backend == "docker":
            print("MATLABProvider: using Docker backend")
        else:
            self._initialize_matlab()

    def _initialize_matlab(self):
        """Initialize MATLAB Engine API."""
        try:
            # Try to import MATLAB engine
            import matlab.engine
            print("MATLAB Engine API found, attempting to start MATLAB...")

            # Try to start MATLAB with different approaches
            try:
                # Method 1: Start with default settings
                self.engine = matlab.engine.start_matlab()
                print("MATLAB Engine started successfully with default settings")
            except Exception as e1:
                print(f"Default MATLAB start failed: {e1}")
                try:
                    # Method 2: Start with specific MATLAB path
                    if self.matlab_path:
                        self.engine = matlab.engine.start_matlab(
                            matlab_path=self.matlab_path)
                        print(
                            f"MATLAB Engine started successfully with path: {
                                self.matlab_path}")
                    else:
                        raise e1
                except Exception as e2:
                    print(f"MATLAB start with custom path failed: {e2}")
                    try:
                        # Method 3: Try to find MATLAB installation
                        matlab_paths = self._find_matlab_installation()
                        if matlab_paths:
                            for path in matlab_paths:
                                try:
                                    self.engine = matlab.engine.start_matlab(
                                        matlab_path=path)
                                    print(
                                        f"MATLAB Engine started successfully with found path: {path}")
                                    break
                                except Exception:
                                    continue
                            else:
                                raise Exception(
                                    "No working MATLAB installation found")
                        else:
                            raise Exception("No MATLAB installation found")
                    except Exception as e3:
                        print(f"All MATLAB start methods failed: {e3}")
                        raise e3

            # Add custom path if specified
            if self.matlab_path and self.engine:
                self.engine.addpath(self.matlab_path)
                print(f"Added custom MATLAB path: {self.matlab_path}")

        except ImportError:
            print("MATLAB Engine API not available - using mock implementation")
            print(
                "To install: pip install matlabengine (requires MATLAB installation)"
            )
            self.engine = None
        except Exception as e:
            print(
                f"Failed to initialize MATLAB: {e} - using mock implementation")
            print("Please ensure MATLAB R2024a is installed and accessible")
            self.engine = None

    def _find_matlab_installation(self):
        """Find MATLAB installation paths."""
        import os
        import glob

        possible_paths = []

        # Common MATLAB installation paths
        search_paths = [
            "/usr/local/MATLAB/*",
            "/opt/MATLAB/*",
            "/Applications/MATLAB_*.app",
            "/usr/local/bin/matlab",
            "/opt/bin/matlab"
        ]

        for pattern in search_paths:
            matches = glob.glob(pattern)
            possible_paths.extend(matches)

        # Check environment variables
        matlab_root = os.environ.get('MATLAB_ROOT')
        if matlab_root and os.path.exists(matlab_root):
            possible_paths.append(matlab_root)

        # Check PATH for matlab executable
        import shutil
        matlab_exe = shutil.which('matlab')
        if matlab_exe:
            matlab_dir = os.path.dirname(os.path.dirname(matlab_exe))
            possible_paths.append(matlab_dir)

        return possible_paths

    def compute(self, query: str) -> ComputationResult:
        """Execute computation using MATLAB."""
        start_time = time.time()

        try:
            # Docker backend preferred when configured
            if self.backend == "docker":
                result = self._docker_compute(query)
                execution_time = time.time() - start_time
                self._record_execution(execution_time)
                return result

            if self.engine is None:
                # Use mock implementation for development
                return self._mock_compute(query)

            # Parse query and determine MATLAB function to call
            matlab_function = self._parse_query_to_matlab_function(query)

            # Execute MATLAB function
            result = matlab_function()

            # Extract different output formats
            plaintext = str(result)
            latex = self._convert_to_latex(result)
            mathml = self._convert_to_mathml(result)

            # Generate visualization if applicable
            images = self._generate_visualizations(result, query)

            execution_time = time.time() - start_time
            self._record_execution(execution_time)

            return ComputationResult(
                plaintext=plaintext,
                latex=latex,
                mathml=mathml,
                images=images,
                provider='matlab',
                cost=0.0,  # Local license
                execution_time=execution_time,
                query=query
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_execution(execution_time)
            raise ComputationError(f"MATLAB computation failed: {e}")

    def _docker_compute(self, query: str) -> ComputationResult:
        """Execute computation using a running MATLAB Docker container.

        Requires:
          - self.container_name: name of the running container
          - self.work_mount: host path mounted as /work in the container
          - self.entrypoint: path to entrypoint.m on the host (copied into job dir)
        """
        if not self.container_name or not self.work_mount:
            raise ComputationError(
                "Docker backend not configured: container_name and work_mount are required")

        job_id = str(uuid.uuid4())
        job_dir = os.path.join(self.work_mount, "jobs", job_id)
        os.makedirs(job_dir, exist_ok=True)

        # Prepare input.json
        input_path = os.path.join(job_dir, "input.json")
        with open(input_path, "w") as f:
            json.dump({"query": query}, f)

        # Ensure entrypoint.m is present in job directory
        entrypoint_host = self.entrypoint or os.path.join(
            self.work_mount, "entrypoint.m")
        entrypoint_dest = os.path.join(job_dir, "entrypoint.m")
        if os.path.exists(entrypoint_host):
            try:
                shutil.copy2(entrypoint_host, entrypoint_dest)
            except Exception as e:
                raise ComputationError(f"Failed to copy entrypoint.m: {e}")
        else:
            # Write a minimal numeric entrypoint as fallback
            try:
                with open(entrypoint_dest, "w") as f:
                    f.write(
                        """
function entrypoint()
  try
    inpath = fullfile(pwd, 'input.json');
    params = struct();
    if exist(inpath,'file')==2, params = jsondecode(fileread(inpath)); end
    tic;
    syms x; y = int(exp(-x^2), -inf, inf); % requires Symbolic toolbox
    elapsed = toc;
    out = struct('plaintext', char(y), 'latex', latex(y), 'provider','matlab', 'execution_time', elapsed);
    fid=fopen('result.json','w'); fwrite(fid,jsonencode(out)); fclose(fid);
  catch ME
    fid=fopen('result.json','w'); fwrite(fid,jsonencode(struct('error',ME.message))); fclose(fid);
    rethrow(ME);
  end
end
""".strip()
                    )
            except Exception as e:
                raise ComputationError(
                    f"Failed to write fallback entrypoint.m: {e}")

        # Compute the container-side working directory corresponding to job_dir
        # Host job_dir is under self.work_mount; inside container it's under
        # /work
        if not job_dir.startswith(self.work_mount.rstrip("/")):
            raise ComputationError(
                "job_dir is not under work_mount; cannot map to container path")
        rel = job_dir[len(self.work_mount.rstrip("/")):].lstrip("/")
        container_workdir = os.path.join("/work", rel)

        # Run MATLAB in the container
        cmd = [
            "docker", "exec", "-w", container_workdir,
            self.container_name,
            "matlab", "-batch", "entrypoint",
        ]
        try:
            completed = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=600)
        except subprocess.TimeoutExpired:
            raise ComputationError("MATLAB docker job timed out")
        except Exception as e:
            raise ComputationError(f"Failed to execute docker job: {e}")

        if completed.returncode != 0:
            raise ComputationError(
                f"MATLAB docker job failed: {
                    completed.stderr.strip() or completed.stdout.strip()}")

        # Read result.json
        result_path = os.path.join(job_dir, "result.json")
        if not os.path.exists(result_path):
            raise ComputationError(
                "MATLAB docker job did not produce result.json")

        try:
            with open(result_path, "r") as f:
                res = json.load(f)
        except Exception as e:
            raise ComputationError(f"Failed to parse result.json: {e}")

        if isinstance(res, dict) and "error" in res:
            raise ComputationError(f"MATLAB error: {res['error']}")

        plaintext = res.get("plaintext") or ""
        latex = res.get("latex") or ""
        images: List[str] = []

        return ComputationResult(
            plaintext=plaintext,
            latex=latex,
            mathml=None,
            images=images,
            provider="matlab",
            cost=0.0,
            execution_time=res.get("execution_time", 0.0),
            query=query,
        )

    def _mock_compute(self, query: str) -> ComputationResult:
        """Mock MATLAB computation for development/testing."""
        start_time = time.time()

        # Simple mock responses based on query content
        query_lower = query.lower()

        if 'solve' in query_lower or '=' in query:
            # Mock equation solving
            plaintext = "x = -1, x = 2"  # Mock solution
            latex = r"x = -1, \quad x = 2"
            mathml = "<math><mi>x</mi><mo>=</mo><mn>-1</mn><mo>,</mo><mi>x</mi><mo>=</mo><mn>2</mn></math>"
        elif 'integrate' in query_lower or 'int' in query_lower:
            # Mock integration
            plaintext = "x^3/3 + C"
            latex = r"\frac{x^3}{3} + C"
            mathml = "<math><mfrac><msup><mi>x</mi><mn>3</mn></msup><mn>3</mn></mfrac><mo>+</mo><mi>C</mi></math>"
        elif 'derivative' in query_lower or 'diff' in query_lower:
            # Mock differentiation
            plaintext = "2*x"
            latex = r"2x"
            mathml = "<math><mn>2</mn><mi>x</mi></math>"
        elif 'matrix' in query_lower or 'eigen' in query_lower:
            # Mock matrix operations
            plaintext = "Eigenvalues: [1, 2, 3]"
            latex = r"\lambda = 1, 2, 3"
            mathml = "<math><mi>λ</mi><mo>=</mo><mn>1</mn><mo>,</mo><mn>2</mn><mo>,</mo><mn>3</mn></math>"
        else:
            # Generic mock response
            plaintext = f"MATLAB result for: {query}"
            latex = r"\text{MATLAB result}"
            mathml = "<math><mtext>MATLAB result</mtext></math>"

        execution_time = time.time() - start_time
        self._record_execution(execution_time)

        return ComputationResult(
            plaintext=plaintext,
            latex=latex,
            mathml=mathml,
            images=[],
            provider='matlab_mock',
            cost=0.0,
            execution_time=execution_time,
            query=query
        )

    def _parse_query_to_matlab_function(self, query: str):
        """Parse query and return appropriate MATLAB function."""
        query_lower = query.lower()

        if 'solve' in query_lower or '=' in query_lower:
            # Convert to MATLAB solve syntax
            matlab_query = self._convert_to_matlab_solve(query)
            return lambda: self.engine.eval(matlab_query)
        elif 'integrate' in query_lower or 'int' in query_lower:
            # Convert to MATLAB int syntax
            matlab_query = self._convert_to_matlab_integral(query)
            return lambda: self.engine.eval(matlab_query)
        elif 'derivative' in query_lower or 'diff' in query_lower:
            # Convert to MATLAB diff syntax
            matlab_query = self._convert_to_matlab_diff(query)
            return lambda: self.engine.eval(matlab_query)
        elif 'eigen' in query_lower or 'eigenvalue' in query_lower:
            # Convert to MATLAB eig syntax
            matlab_query = self._convert_to_matlab_eig(query)
            return lambda: self.engine.eval(matlab_query)
        elif 'optimize' in query_lower or 'minimize' in query_lower or 'maximize' in query_lower:
            # Convert to MATLAB optimization syntax
            matlab_query = self._convert_to_matlab_optimize(query)
            return lambda: self.engine.eval(matlab_query)
        elif 'plot' in query_lower or 'graph' in query_lower:
            # Convert to MATLAB plot syntax
            matlab_query = self._convert_to_matlab_plot(query)
            return lambda: self.engine.eval(matlab_query)
        else:
            # Direct evaluation
            return lambda: self.engine.eval(query)

    def _convert_to_matlab_solve(self, query: str) -> str:
        """Convert query to MATLAB solve syntax."""
        # Simple conversion for basic equations
        # Example: "solve x^2 + 2*x + 1 = 0" -> "syms x; solve(x^2 + 2*x + 1 ==
        # 0, x)"
        if '=' in query:
            equation = query.split('solve')[1].strip()
            if '=' in equation:
                left, right = equation.split('=', 1)
                left = left.strip()
                right = right.strip()
                return f"syms x; solve({left} == {right}, x)"
        return f"syms x; solve({query}, x)"

    def _convert_to_matlab_integral(self, query: str) -> str:
        """Convert query to MATLAB integral syntax."""
        # Example: "integrate x^2 from 0 to 1" -> "syms x; int(x^2, x, 0, 1)"
        if 'from' in query and 'to' in query:
            parts = query.split()
            expr = parts[1]  # x^2
            from_idx = parts.index('from')
            to_idx = parts.index('to')
            lower = parts[from_idx + 1]
            upper = parts[to_idx + 1]
            return f"syms x; int({expr}, x, {lower}, {upper})"
        else:
            # Indefinite integral
            expr = query.replace('integrate', '').replace('int', '').strip()
            return f"syms x; int({expr}, x)"

    def _convert_to_matlab_diff(self, query: str) -> str:
        """Convert query to MATLAB diff syntax."""
        # Example: "derivative of x^3" -> "syms x; diff(x^3, x)"
        if 'of' in query:
            expr = query.split('of')[1].strip()
            return f"syms x; diff({expr}, x)"
        else:
            expr = query.replace('derivative', '').replace('diff', '').strip()
            return f"syms x; diff({expr}, x)"

    def _convert_to_matlab_eig(self, query: str) -> str:
        """Convert query to MATLAB eig syntax."""
        # Example: "eigenvalues of [1 2; 3 4]" -> "eig([1 2; 3 4])"
        if 'of' in query:
            matrix = query.split('of')[1].strip()
            return f"eig({matrix})"
        else:
            # Extract matrix from query
            import re
            matrix_match = re.search(r'\[.*?\]', query)
            if matrix_match:
                matrix = matrix_match.group()
                return f"eig({matrix})"
            return "eig([1 2; 3 4])"  # Default matrix

    def _convert_to_matlab_optimize(self, query: str) -> str:
        """Convert query to MATLAB optimization syntax."""
        # Example: "optimize x^2 + 2*x + 1" -> "syms x; f = x^2 + 2*x + 1;
        # fminunc(@(x) x^2 + 2*x + 1, 0)"
        if 'optimize' in query:
            expr = query.replace('optimize', '').strip()
            return f"syms x; f = {expr}; fminunc(@(x) {expr}, 0)"
        return f"syms x; fminunc(@(x) {query}, 0)"

    def _convert_to_matlab_plot(self, query: str) -> str:
        """Convert query to MATLAB plot syntax."""
        # Example: "plot x^2 from -5 to 5" -> "x = -5:0.1:5; y = x.^2; plot(x,
        # y)"
        if 'from' in query and 'to' in query:
            parts = query.split()
            expr = parts[1]  # x^2
            from_idx = parts.index('from')
            to_idx = parts.index('to')
            lower = parts[from_idx + 1]
            upper = parts[to_idx + 1]
            return f"x = {lower}:0.1:{upper}; y = {expr}; plot(x, y)"
        else:
            expr = query.replace('plot', '').replace('graph', '').strip()
            return f"x = -10:0.1:10; y = {expr}; plot(x, y)"

    def _convert_to_latex(self, result) -> str:
        """Convert MATLAB result to LaTeX format."""
        try:
            if self.engine:
                # Try to get LaTeX representation
                latex_result = self.engine.eval(f"latex({result})")
                return str(latex_result)
        except BaseException:
            pass

        # Fallback: convert result to basic LaTeX
        result_str = str(result)
        if isinstance(result, (int, float)):
            return f"${result_str}$"
        elif '[' in result_str and ']' in result_str:
            # Matrix format
            return f"$\\begin{{bmatrix}} {result_str} \\end{{bmatrix}}$"
        else:
            return f"${result_str}$"

    def _convert_to_mathml(self, result) -> str:
        """Convert MATLAB result to MathML format."""
        try:
            if self.engine:
                # Try to get MathML representation
                mathml_result = self.engine.eval(f"mathml({result})")
                return str(mathml_result)
        except BaseException:
            pass

        # Fallback: convert result to basic MathML
        result_str = str(result)
        if isinstance(result, (int, float)):
            return f"<math><mn>{result_str}</mn></math>"
        else:
            return f"<math><mtext>{result_str}</mtext></math>"

    def _generate_visualizations(self, result, query: str) -> List[str]:
        """Generate visualizations for the result."""
        images = []

        # Check if query involves plotting
        if any(keyword in query.lower()
               for keyword in ['plot', 'graph', 'visualize', 'show']):
            # Mock image generation
            images.append(f"matlab_plot_{hash(query) % 1000}.png")

        return images

    def analyze_data(
            self,
            data: List[float],
            analysis_type: str = "basic") -> ComputationResult:
        """Perform data analysis using MATLAB."""
        if self.engine is None:
            # Mock data analysis
            return self._mock_data_analysis(data, analysis_type)

        try:
            # Convert data to MATLAB format
            import matlab
            matlab_data = matlab.double(data)

            if analysis_type == "statistical":
                result = self.engine.stats(matlab_data)
            elif analysis_type == "signal_processing":
                result = self.engine.signal_processing(matlab_data)
            else:
                result = self.engine.basic_stats(matlab_data)

            return ComputationResult(
                plaintext=str(result),
                provider='matlab',
                cost=0.0,
                query=f"Data analysis: {analysis_type}"
            )
        except Exception as e:
            raise ComputationError(f"MATLAB data analysis failed: {e}")

    def _mock_data_analysis(
            self,
            data: List[float],
            analysis_type: str) -> ComputationResult:
        """Mock data analysis for development."""
        import statistics

        if analysis_type == "statistical":
            mean_val = statistics.mean(data)
            std_val = statistics.stdev(data) if len(data) > 1 else 0
            plaintext = f"Mean: {mean_val:.4f}, Std: {std_val:.4f}"
        else:
            plaintext = f"Basic analysis of {len(data)} data points"

        return ComputationResult(
            plaintext=plaintext,
            provider='matlab_mock',
            cost=0.0,
            query=f"Data analysis: {analysis_type}"
        )
