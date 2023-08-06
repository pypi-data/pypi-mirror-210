# Copyright 2023 Sony Semiconductor Israel, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from model_compression_toolkit.quantizers_infrastructure.inferable_infrastructure.pytorch.quantizers.activation_inferable_quantizers.activation_pot_inferable_quantizer \
    import ActivationPOTInferableQuantizer
from model_compression_toolkit.quantizers_infrastructure.inferable_infrastructure.pytorch.quantizers.activation_inferable_quantizers.activation_symmetric_inferable_quantizer \
    import ActivationSymmetricInferableQuantizer
from model_compression_toolkit.quantizers_infrastructure.inferable_infrastructure.pytorch.quantizers.activation_inferable_quantizers.activation_uniform_inferable_quantizer \
    import ActivationUniformInferableQuantizer
from model_compression_toolkit.quantizers_infrastructure.inferable_infrastructure.pytorch.quantizers.activation_inferable_quantizers.activation_lut_pot_inferable_quantizer \
    import ActivationLutPOTInferableQuantizer
from model_compression_toolkit.quantizers_infrastructure.inferable_infrastructure.pytorch.quantizers.base_pytorch_inferable_quantizer \
    import BasePyTorchInferableQuantizer
from model_compression_toolkit.quantizers_infrastructure.inferable_infrastructure.pytorch.quantizers.weights_inferable_quantizers.weights_pot_inferable_quantizer \
    import WeightsPOTInferableQuantizer
from model_compression_toolkit.quantizers_infrastructure.inferable_infrastructure.pytorch.quantizers.weights_inferable_quantizers.weights_symmetric_inferable_quantizer \
    import WeightsSymmetricInferableQuantizer
from model_compression_toolkit.quantizers_infrastructure.inferable_infrastructure.pytorch.quantizers.weights_inferable_quantizers.weights_uniform_inferable_quantizer \
    import WeightsUniformInferableQuantizer
from model_compression_toolkit.quantizers_infrastructure.inferable_infrastructure.pytorch.quantizers.weights_inferable_quantizers.weights_lut_symmetric_inferable_quantizer \
    import WeightsLUTSymmetricInferableQuantizer
from model_compression_toolkit.quantizers_infrastructure.inferable_infrastructure.pytorch.quantizers.weights_inferable_quantizers.weights_lut_pot_inferable_quantizer \
    import WeightsLUTPOTInferableQuantizer
