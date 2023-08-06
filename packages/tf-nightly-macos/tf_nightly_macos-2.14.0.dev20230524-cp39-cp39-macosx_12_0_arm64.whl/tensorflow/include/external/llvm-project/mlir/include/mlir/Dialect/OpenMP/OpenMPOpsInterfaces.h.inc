/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Declarations                                                     *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace omp {
class OutlineableOpenMPOpInterface;
namespace detail {
struct OutlineableOpenMPOpInterfaceInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
    ::mlir::Block*(*getAllocaBlock)(const Concept *impl, ::mlir::Operation *);
  };
  template<typename ConcreteOp>
  class Model : public Concept {
  public:
    using Interface = ::mlir::omp::OutlineableOpenMPOpInterface;
    Model() : Concept{getAllocaBlock} {}

    static inline ::mlir::Block*getAllocaBlock(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteOp>
  class FallbackModel : public Concept {
  public:
    using Interface = ::mlir::omp::OutlineableOpenMPOpInterface;
    FallbackModel() : Concept{getAllocaBlock} {}

    static inline ::mlir::Block*getAllocaBlock(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteModel, typename ConcreteOp>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteOp;
  };
};template <typename ConcreteOp>
struct OutlineableOpenMPOpInterfaceTrait;

} // namespace detail
class OutlineableOpenMPOpInterface : public ::mlir::OpInterface<OutlineableOpenMPOpInterface, detail::OutlineableOpenMPOpInterfaceInterfaceTraits> {
public:
  using ::mlir::OpInterface<OutlineableOpenMPOpInterface, detail::OutlineableOpenMPOpInterfaceInterfaceTraits>::OpInterface;
  template <typename ConcreteOp>
  struct Trait : public detail::OutlineableOpenMPOpInterfaceTrait<ConcreteOp> {};
  /// Get alloca block
  ::mlir::Block*getAllocaBlock();
};
namespace detail {
  template <typename ConcreteOp>
  struct OutlineableOpenMPOpInterfaceTrait : public ::mlir::OpInterface<OutlineableOpenMPOpInterface, detail::OutlineableOpenMPOpInterfaceInterfaceTraits>::Trait<ConcreteOp> {
  };
}// namespace detail
} // namespace omp
} // namespace mlir
namespace mlir {
namespace omp {
class ReductionClauseInterface;
namespace detail {
struct ReductionClauseInterfaceInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
    ::mlir::SmallVector<::mlir::Value> (*getAllReductionVars)(const Concept *impl, ::mlir::Operation *);
  };
  template<typename ConcreteOp>
  class Model : public Concept {
  public:
    using Interface = ::mlir::omp::ReductionClauseInterface;
    Model() : Concept{getAllReductionVars} {}

    static inline ::mlir::SmallVector<::mlir::Value> getAllReductionVars(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteOp>
  class FallbackModel : public Concept {
  public:
    using Interface = ::mlir::omp::ReductionClauseInterface;
    FallbackModel() : Concept{getAllReductionVars} {}

    static inline ::mlir::SmallVector<::mlir::Value> getAllReductionVars(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteModel, typename ConcreteOp>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteOp;
    ::mlir::SmallVector<::mlir::Value> getAllReductionVars(::mlir::Operation *tablegen_opaque_val) const;
  };
};template <typename ConcreteOp>
struct ReductionClauseInterfaceTrait;

} // namespace detail
class ReductionClauseInterface : public ::mlir::OpInterface<ReductionClauseInterface, detail::ReductionClauseInterfaceInterfaceTraits> {
public:
  using ::mlir::OpInterface<ReductionClauseInterface, detail::ReductionClauseInterfaceInterfaceTraits>::OpInterface;
  template <typename ConcreteOp>
  struct Trait : public detail::ReductionClauseInterfaceTrait<ConcreteOp> {};
  /// Get reduction vars
  ::mlir::SmallVector<::mlir::Value> getAllReductionVars();
};
namespace detail {
  template <typename ConcreteOp>
  struct ReductionClauseInterfaceTrait : public ::mlir::OpInterface<ReductionClauseInterface, detail::ReductionClauseInterfaceInterfaceTraits>::Trait<ConcreteOp> {
    /// Get reduction vars
    ::mlir::SmallVector<::mlir::Value> getAllReductionVars() {
      return (*static_cast<ConcreteOp *>(this)).getReductionVars();
    }
  };
}// namespace detail
} // namespace omp
} // namespace mlir
namespace mlir {
namespace omp {
class DeclareTargetInterface;
namespace detail {
struct DeclareTargetInterfaceInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
    void (*setDeclareTarget)(const Concept *impl, ::mlir::Operation *, mlir::omp::DeclareTargetDeviceType, mlir::omp::DeclareTargetCaptureClause);
    bool (*isDeclareTarget)(const Concept *impl, ::mlir::Operation *);
    mlir::omp::DeclareTargetDeviceType (*getDeclareTargetDeviceType)(const Concept *impl, ::mlir::Operation *);
    mlir::omp::DeclareTargetCaptureClause (*getDeclareTargetCaptureClause)(const Concept *impl, ::mlir::Operation *);
  };
  template<typename ConcreteOp>
  class Model : public Concept {
  public:
    using Interface = ::mlir::omp::DeclareTargetInterface;
    Model() : Concept{setDeclareTarget, isDeclareTarget, getDeclareTargetDeviceType, getDeclareTargetCaptureClause} {}

    static inline void setDeclareTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, mlir::omp::DeclareTargetDeviceType deviceType, mlir::omp::DeclareTargetCaptureClause captureClause);
    static inline bool isDeclareTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline mlir::omp::DeclareTargetDeviceType getDeclareTargetDeviceType(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline mlir::omp::DeclareTargetCaptureClause getDeclareTargetCaptureClause(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteOp>
  class FallbackModel : public Concept {
  public:
    using Interface = ::mlir::omp::DeclareTargetInterface;
    FallbackModel() : Concept{setDeclareTarget, isDeclareTarget, getDeclareTargetDeviceType, getDeclareTargetCaptureClause} {}

    static inline void setDeclareTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, mlir::omp::DeclareTargetDeviceType deviceType, mlir::omp::DeclareTargetCaptureClause captureClause);
    static inline bool isDeclareTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline mlir::omp::DeclareTargetDeviceType getDeclareTargetDeviceType(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline mlir::omp::DeclareTargetCaptureClause getDeclareTargetCaptureClause(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteModel, typename ConcreteOp>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteOp;
    void setDeclareTarget(::mlir::Operation *tablegen_opaque_val, mlir::omp::DeclareTargetDeviceType deviceType, mlir::omp::DeclareTargetCaptureClause captureClause) const;
    bool isDeclareTarget(::mlir::Operation *tablegen_opaque_val) const;
    mlir::omp::DeclareTargetDeviceType getDeclareTargetDeviceType(::mlir::Operation *tablegen_opaque_val) const;
    mlir::omp::DeclareTargetCaptureClause getDeclareTargetCaptureClause(::mlir::Operation *tablegen_opaque_val) const;
  };
};template <typename ConcreteOp>
struct DeclareTargetInterfaceTrait;

} // namespace detail
class DeclareTargetInterface : public ::mlir::OpInterface<DeclareTargetInterface, detail::DeclareTargetInterfaceInterfaceTraits> {
public:
  using ::mlir::OpInterface<DeclareTargetInterface, detail::DeclareTargetInterfaceInterfaceTraits>::OpInterface;
  template <typename ConcreteOp>
  struct Trait : public detail::DeclareTargetInterfaceTrait<ConcreteOp> {};
  /// Set the declare target attribute on the current operation with the
  /// specified attribute arguments.
  void setDeclareTarget(mlir::omp::DeclareTargetDeviceType deviceType, mlir::omp::DeclareTargetCaptureClause captureClause);
  /// Checks if the declare target attribute has been applied and exists on the
  /// current operation. Returns true if it exists on it, otherwise returns
  /// false.
  bool isDeclareTarget();
  /// Returns the DeclareTargetDeviceType segment of the DeclareTarget attribute if it
  /// exists on the current operation. Otherwise it returns null.
  mlir::omp::DeclareTargetDeviceType getDeclareTargetDeviceType();
  /// Returns the DeclareTargetCaptureClause segment of the DeclareTarget attribute if it
  /// exists on the current operation. Otherwise it returns null.
  mlir::omp::DeclareTargetCaptureClause getDeclareTargetCaptureClause();
};
namespace detail {
  template <typename ConcreteOp>
  struct DeclareTargetInterfaceTrait : public ::mlir::OpInterface<DeclareTargetInterface, detail::DeclareTargetInterfaceInterfaceTraits>::Trait<ConcreteOp> {
    /// Set the declare target attribute on the current operation with the
    /// specified attribute arguments.
    void setDeclareTarget(mlir::omp::DeclareTargetDeviceType deviceType, mlir::omp::DeclareTargetCaptureClause captureClause) {
      (*static_cast<ConcreteOp *>(this))->setAttr("omp.declare_target",
                  mlir::omp::DeclareTargetAttr::get(
                      (*static_cast<ConcreteOp *>(this))->getContext(),
                      mlir::omp::DeclareTargetDeviceTypeAttr::get(
                          (*static_cast<ConcreteOp *>(this))->getContext(), deviceType),
                      mlir::omp::DeclareTargetCaptureClauseAttr::get(
                          (*static_cast<ConcreteOp *>(this))->getContext(), captureClause)));
    }
    /// Checks if the declare target attribute has been applied and exists on the
    /// current operation. Returns true if it exists on it, otherwise returns
    /// false.
    bool isDeclareTarget() {
      return (*static_cast<ConcreteOp *>(this))->hasAttr("omp.declare_target");
    }
    /// Returns the DeclareTargetDeviceType segment of the DeclareTarget attribute if it
    /// exists on the current operation. Otherwise it returns null.
    mlir::omp::DeclareTargetDeviceType getDeclareTargetDeviceType() {
      if (mlir::Attribute dTar = (*static_cast<ConcreteOp *>(this))->getAttr("omp.declare_target"))
          if (auto dAttr = dTar.dyn_cast_or_null<mlir::omp::DeclareTargetAttr>())
            return dAttr.getDeviceType().getValue();
        return {};
    }
    /// Returns the DeclareTargetCaptureClause segment of the DeclareTarget attribute if it
    /// exists on the current operation. Otherwise it returns null.
    mlir::omp::DeclareTargetCaptureClause getDeclareTargetCaptureClause() {
      if (mlir::Attribute dTar = (*static_cast<ConcreteOp *>(this))->getAttr("omp.declare_target"))
          if (auto dAttr = dTar.dyn_cast_or_null<mlir::omp::DeclareTargetAttr>())
            return dAttr.getCaptureClause().getValue();
        return {};
    }
  };
}// namespace detail
} // namespace omp
} // namespace mlir
namespace mlir {
namespace omp {
class OffloadModuleInterface;
namespace detail {
struct OffloadModuleInterfaceInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
    void (*setIsDevice)(const Concept *impl, ::mlir::Operation *, bool);
    bool (*getIsDevice)(const Concept *impl, ::mlir::Operation *);
    mlir::omp::FlagsAttr (*getFlags)(const Concept *impl, ::mlir::Operation *);
    void (*setFlags)(const Concept *impl, ::mlir::Operation *, uint32_t, bool, bool, bool, bool, uint32_t);
    mlir::omp::TargetAttr (*getTarget)(const Concept *impl, ::mlir::Operation *);
    void (*setTarget)(const Concept *impl, ::mlir::Operation *, llvm::StringRef, llvm::StringRef);
    void (*setHostIRFilePath)(const Concept *impl, ::mlir::Operation *, std::string);
    llvm::StringRef (*getHostIRFilePath)(const Concept *impl, ::mlir::Operation *);
  };
  template<typename ConcreteOp>
  class Model : public Concept {
  public:
    using Interface = ::mlir::omp::OffloadModuleInterface;
    Model() : Concept{setIsDevice, getIsDevice, getFlags, setFlags, getTarget, setTarget, setHostIRFilePath, getHostIRFilePath} {}

    static inline void setIsDevice(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, bool isDevice);
    static inline bool getIsDevice(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline mlir::omp::FlagsAttr getFlags(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline void setFlags(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, uint32_t debugKind, bool assumeTeamsOversubscription, bool assumeThreadsOversubscription, bool assumeNoThreadState, bool assumeNoNestedParallelism, uint32_t openmpDeviceVersion);
    static inline mlir::omp::TargetAttr getTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline void setTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, llvm::StringRef targetCPU, llvm::StringRef targetFeatures);
    static inline void setHostIRFilePath(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, std::string hostIRFilePath);
    static inline llvm::StringRef getHostIRFilePath(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteOp>
  class FallbackModel : public Concept {
  public:
    using Interface = ::mlir::omp::OffloadModuleInterface;
    FallbackModel() : Concept{setIsDevice, getIsDevice, getFlags, setFlags, getTarget, setTarget, setHostIRFilePath, getHostIRFilePath} {}

    static inline void setIsDevice(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, bool isDevice);
    static inline bool getIsDevice(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline mlir::omp::FlagsAttr getFlags(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline void setFlags(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, uint32_t debugKind, bool assumeTeamsOversubscription, bool assumeThreadsOversubscription, bool assumeNoThreadState, bool assumeNoNestedParallelism, uint32_t openmpDeviceVersion);
    static inline mlir::omp::TargetAttr getTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline void setTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, llvm::StringRef targetCPU, llvm::StringRef targetFeatures);
    static inline void setHostIRFilePath(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, std::string hostIRFilePath);
    static inline llvm::StringRef getHostIRFilePath(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteModel, typename ConcreteOp>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteOp;
    void setIsDevice(::mlir::Operation *tablegen_opaque_val, bool isDevice) const;
    bool getIsDevice(::mlir::Operation *tablegen_opaque_val) const;
    mlir::omp::FlagsAttr getFlags(::mlir::Operation *tablegen_opaque_val) const;
    void setFlags(::mlir::Operation *tablegen_opaque_val, uint32_t debugKind, bool assumeTeamsOversubscription, bool assumeThreadsOversubscription, bool assumeNoThreadState, bool assumeNoNestedParallelism, uint32_t openmpDeviceVersion) const;
    mlir::omp::TargetAttr getTarget(::mlir::Operation *tablegen_opaque_val) const;
    void setTarget(::mlir::Operation *tablegen_opaque_val, llvm::StringRef targetCPU, llvm::StringRef targetFeatures) const;
    void setHostIRFilePath(::mlir::Operation *tablegen_opaque_val, std::string hostIRFilePath) const;
    llvm::StringRef getHostIRFilePath(::mlir::Operation *tablegen_opaque_val) const;
  };
};template <typename ConcreteOp>
struct OffloadModuleInterfaceTrait;

} // namespace detail
class OffloadModuleInterface : public ::mlir::OpInterface<OffloadModuleInterface, detail::OffloadModuleInterfaceInterfaceTraits> {
public:
  using ::mlir::OpInterface<OffloadModuleInterface, detail::OffloadModuleInterfaceInterfaceTraits>::OpInterface;
  template <typename ConcreteOp>
  struct Trait : public detail::OffloadModuleInterfaceTrait<ConcreteOp> {};
  /// Set the attribute IsDeviceAttr on the current module with the
  /// specified boolean argument.
  void setIsDevice(bool isDevice);
  /// Get the IsDeviceAttr attribute on the current module if it exists and return
  /// its value, if it doesn't exist it returns false by default.
  bool getIsDevice();
  /// Get the FlagsAttr attribute on the current module if it exists
  /// and return the attribute, if it doesn't exit it returns a nullptr
  mlir::omp::FlagsAttr getFlags();
  /// Apply an omp.FlagsAttr to a module with the specified values
  /// for the flags
  void setFlags(uint32_t debugKind, bool assumeTeamsOversubscription, bool assumeThreadsOversubscription, bool assumeNoThreadState, bool assumeNoNestedParallelism, uint32_t openmpDeviceVersion);
  /// Get the Target attribute on the current module if it exists
  /// and return the attribute, if it doesn't exist it returns a nullptr.
  mlir::omp::TargetAttr getTarget();
  /// Set the attribute target on the current module with the
  /// specified string arguments - name of cpu and corresponding features.
  void setTarget(llvm::StringRef targetCPU, llvm::StringRef targetFeatures);
  /// Set a StringAttr on the current module containing the host IR file path. This
  /// file path is used in two-phase compilation during the device phase to generate
  /// device side LLVM IR when lowering MLIR.
  void setHostIRFilePath(std::string hostIRFilePath);
  /// Find the host-ir file path StringAttr from the current module if it exists and
  /// return its contained value, if it doesn't exist it returns an empty string. This
  /// file path is used in two-phase compilation during the device phase to generate
  /// device side LLVM IR when lowering MLIR.
  llvm::StringRef getHostIRFilePath();
};
namespace detail {
  template <typename ConcreteOp>
  struct OffloadModuleInterfaceTrait : public ::mlir::OpInterface<OffloadModuleInterface, detail::OffloadModuleInterfaceInterfaceTraits>::Trait<ConcreteOp> {
    /// Set the attribute IsDeviceAttr on the current module with the
    /// specified boolean argument.
    void setIsDevice(bool isDevice) {
      (*static_cast<ConcreteOp *>(this))->setAttr(
          mlir::StringAttr::get((*static_cast<ConcreteOp *>(this))->getContext(), llvm::Twine{"omp.is_device"}),
            mlir::omp::IsDeviceAttr::get((*static_cast<ConcreteOp *>(this))->getContext(), isDevice));
    }
    /// Get the IsDeviceAttr attribute on the current module if it exists and return
    /// its value, if it doesn't exist it returns false by default.
    bool getIsDevice() {
      if (Attribute isDevice = (*static_cast<ConcreteOp *>(this))->getAttr("omp.is_device"))
          if (::llvm::isa<mlir::omp::IsDeviceAttr>(isDevice))
            return ::llvm::dyn_cast<IsDeviceAttr>(isDevice).getIsDevice();
        return false;
    }
    /// Get the FlagsAttr attribute on the current module if it exists
    /// and return the attribute, if it doesn't exit it returns a nullptr
    mlir::omp::FlagsAttr getFlags() {
      if (Attribute flags = (*static_cast<ConcreteOp *>(this))->getAttr("omp.flags"))
          return flags.dyn_cast_or_null<mlir::omp::FlagsAttr>();
        return nullptr;
    }
    /// Apply an omp.FlagsAttr to a module with the specified values
    /// for the flags
    void setFlags(uint32_t debugKind, bool assumeTeamsOversubscription, bool assumeThreadsOversubscription, bool assumeNoThreadState, bool assumeNoNestedParallelism, uint32_t openmpDeviceVersion) {
      (*static_cast<ConcreteOp *>(this))->setAttr(("omp." + mlir::omp::FlagsAttr::getMnemonic()).str(),
                  mlir::omp::FlagsAttr::get((*static_cast<ConcreteOp *>(this))->getContext(), debugKind,
                      assumeTeamsOversubscription, assumeThreadsOversubscription,
                      assumeNoThreadState, assumeNoNestedParallelism, openmpDeviceVersion));
    }
    /// Get the Target attribute on the current module if it exists
    /// and return the attribute, if it doesn't exist it returns a nullptr.
    mlir::omp::TargetAttr getTarget() {
      if (Attribute flags = (*static_cast<ConcreteOp *>(this))->getAttr("omp.target"))
          return flags.dyn_cast_or_null<mlir::omp::TargetAttr>();
        return nullptr;
    }
    /// Set the attribute target on the current module with the
    /// specified string arguments - name of cpu and corresponding features.
    void setTarget(llvm::StringRef targetCPU, llvm::StringRef targetFeatures) {
      if (targetCPU.empty())
          return;
        (*static_cast<ConcreteOp *>(this))->setAttr(("omp." + mlir::omp::TargetAttr::getMnemonic()).str(),
                  mlir::omp::TargetAttr::get((*static_cast<ConcreteOp *>(this))->getContext(),
                                             targetCPU.str(),
                                             targetFeatures.str()));
    }
    /// Set a StringAttr on the current module containing the host IR file path. This
    /// file path is used in two-phase compilation during the device phase to generate
    /// device side LLVM IR when lowering MLIR.
    void setHostIRFilePath(std::string hostIRFilePath) {
      (*static_cast<ConcreteOp *>(this))->setAttr(
          mlir::StringAttr::get((*static_cast<ConcreteOp *>(this))->getContext(), llvm::Twine{"omp.host_ir_filepath"}),
            mlir::StringAttr::get((*static_cast<ConcreteOp *>(this))->getContext(), hostIRFilePath));
    }
    /// Find the host-ir file path StringAttr from the current module if it exists and
    /// return its contained value, if it doesn't exist it returns an empty string. This
    /// file path is used in two-phase compilation during the device phase to generate
    /// device side LLVM IR when lowering MLIR.
    llvm::StringRef getHostIRFilePath() {
      if (Attribute filepath = (*static_cast<ConcreteOp *>(this))->getAttr("omp.host_ir_filepath"))
          if (::llvm::isa<mlir::StringAttr>(filepath))
            return ::llvm::dyn_cast<mlir::StringAttr>(filepath).getValue();
        return {};
    }
  };
}// namespace detail
} // namespace omp
} // namespace mlir
namespace mlir {
namespace omp {
template<typename ConcreteOp>
::mlir::Block*detail::OutlineableOpenMPOpInterfaceInterfaceTraits::Model<ConcreteOp>::getAllocaBlock(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return &(llvm::cast<ConcreteOp>(tablegen_opaque_val)).getRegion().front();
}
template<typename ConcreteOp>
::mlir::Block*detail::OutlineableOpenMPOpInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getAllocaBlock(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getAllocaBlock(tablegen_opaque_val);
}
} // namespace omp
} // namespace mlir
namespace mlir {
namespace omp {
template<typename ConcreteOp>
::mlir::SmallVector<::mlir::Value> detail::ReductionClauseInterfaceInterfaceTraits::Model<ConcreteOp>::getAllReductionVars(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getAllReductionVars();
}
template<typename ConcreteOp>
::mlir::SmallVector<::mlir::Value> detail::ReductionClauseInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getAllReductionVars(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getAllReductionVars(tablegen_opaque_val);
}
template<typename ConcreteModel, typename ConcreteOp>
::mlir::SmallVector<::mlir::Value> detail::ReductionClauseInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::getAllReductionVars(::mlir::Operation *tablegen_opaque_val) const {
return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getReductionVars();
}
} // namespace omp
} // namespace mlir
namespace mlir {
namespace omp {
template<typename ConcreteOp>
void detail::DeclareTargetInterfaceInterfaceTraits::Model<ConcreteOp>::setDeclareTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, mlir::omp::DeclareTargetDeviceType deviceType, mlir::omp::DeclareTargetCaptureClause captureClause) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).setDeclareTarget(deviceType, captureClause);
}
template<typename ConcreteOp>
bool detail::DeclareTargetInterfaceInterfaceTraits::Model<ConcreteOp>::isDeclareTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).isDeclareTarget();
}
template<typename ConcreteOp>
mlir::omp::DeclareTargetDeviceType detail::DeclareTargetInterfaceInterfaceTraits::Model<ConcreteOp>::getDeclareTargetDeviceType(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getDeclareTargetDeviceType();
}
template<typename ConcreteOp>
mlir::omp::DeclareTargetCaptureClause detail::DeclareTargetInterfaceInterfaceTraits::Model<ConcreteOp>::getDeclareTargetCaptureClause(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getDeclareTargetCaptureClause();
}
template<typename ConcreteOp>
void detail::DeclareTargetInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::setDeclareTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, mlir::omp::DeclareTargetDeviceType deviceType, mlir::omp::DeclareTargetCaptureClause captureClause) {
  return static_cast<const ConcreteOp *>(impl)->setDeclareTarget(tablegen_opaque_val, deviceType, captureClause);
}
template<typename ConcreteOp>
bool detail::DeclareTargetInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::isDeclareTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->isDeclareTarget(tablegen_opaque_val);
}
template<typename ConcreteOp>
mlir::omp::DeclareTargetDeviceType detail::DeclareTargetInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getDeclareTargetDeviceType(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getDeclareTargetDeviceType(tablegen_opaque_val);
}
template<typename ConcreteOp>
mlir::omp::DeclareTargetCaptureClause detail::DeclareTargetInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getDeclareTargetCaptureClause(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getDeclareTargetCaptureClause(tablegen_opaque_val);
}
template<typename ConcreteModel, typename ConcreteOp>
void detail::DeclareTargetInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::setDeclareTarget(::mlir::Operation *tablegen_opaque_val, mlir::omp::DeclareTargetDeviceType deviceType, mlir::omp::DeclareTargetCaptureClause captureClause) const {
(llvm::cast<ConcreteOp>(tablegen_opaque_val))->setAttr("omp.declare_target",
                  mlir::omp::DeclareTargetAttr::get(
                      (llvm::cast<ConcreteOp>(tablegen_opaque_val))->getContext(),
                      mlir::omp::DeclareTargetDeviceTypeAttr::get(
                          (llvm::cast<ConcreteOp>(tablegen_opaque_val))->getContext(), deviceType),
                      mlir::omp::DeclareTargetCaptureClauseAttr::get(
                          (llvm::cast<ConcreteOp>(tablegen_opaque_val))->getContext(), captureClause)));
}
template<typename ConcreteModel, typename ConcreteOp>
bool detail::DeclareTargetInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::isDeclareTarget(::mlir::Operation *tablegen_opaque_val) const {
return (llvm::cast<ConcreteOp>(tablegen_opaque_val))->hasAttr("omp.declare_target");
}
template<typename ConcreteModel, typename ConcreteOp>
mlir::omp::DeclareTargetDeviceType detail::DeclareTargetInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::getDeclareTargetDeviceType(::mlir::Operation *tablegen_opaque_val) const {
if (mlir::Attribute dTar = (llvm::cast<ConcreteOp>(tablegen_opaque_val))->getAttr("omp.declare_target"))
          if (auto dAttr = dTar.dyn_cast_or_null<mlir::omp::DeclareTargetAttr>())
            return dAttr.getDeviceType().getValue();
        return {};
}
template<typename ConcreteModel, typename ConcreteOp>
mlir::omp::DeclareTargetCaptureClause detail::DeclareTargetInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::getDeclareTargetCaptureClause(::mlir::Operation *tablegen_opaque_val) const {
if (mlir::Attribute dTar = (llvm::cast<ConcreteOp>(tablegen_opaque_val))->getAttr("omp.declare_target"))
          if (auto dAttr = dTar.dyn_cast_or_null<mlir::omp::DeclareTargetAttr>())
            return dAttr.getCaptureClause().getValue();
        return {};
}
} // namespace omp
} // namespace mlir
namespace mlir {
namespace omp {
template<typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::Model<ConcreteOp>::setIsDevice(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, bool isDevice) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).setIsDevice(isDevice);
}
template<typename ConcreteOp>
bool detail::OffloadModuleInterfaceInterfaceTraits::Model<ConcreteOp>::getIsDevice(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getIsDevice();
}
template<typename ConcreteOp>
mlir::omp::FlagsAttr detail::OffloadModuleInterfaceInterfaceTraits::Model<ConcreteOp>::getFlags(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getFlags();
}
template<typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::Model<ConcreteOp>::setFlags(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, uint32_t debugKind, bool assumeTeamsOversubscription, bool assumeThreadsOversubscription, bool assumeNoThreadState, bool assumeNoNestedParallelism, uint32_t openmpDeviceVersion) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).setFlags(debugKind, assumeTeamsOversubscription, assumeThreadsOversubscription, assumeNoThreadState, assumeNoNestedParallelism, openmpDeviceVersion);
}
template<typename ConcreteOp>
mlir::omp::TargetAttr detail::OffloadModuleInterfaceInterfaceTraits::Model<ConcreteOp>::getTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getTarget();
}
template<typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::Model<ConcreteOp>::setTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, llvm::StringRef targetCPU, llvm::StringRef targetFeatures) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).setTarget(targetCPU, targetFeatures);
}
template<typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::Model<ConcreteOp>::setHostIRFilePath(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, std::string hostIRFilePath) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).setHostIRFilePath(hostIRFilePath);
}
template<typename ConcreteOp>
llvm::StringRef detail::OffloadModuleInterfaceInterfaceTraits::Model<ConcreteOp>::getHostIRFilePath(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getHostIRFilePath();
}
template<typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::setIsDevice(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, bool isDevice) {
  return static_cast<const ConcreteOp *>(impl)->setIsDevice(tablegen_opaque_val, isDevice);
}
template<typename ConcreteOp>
bool detail::OffloadModuleInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getIsDevice(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getIsDevice(tablegen_opaque_val);
}
template<typename ConcreteOp>
mlir::omp::FlagsAttr detail::OffloadModuleInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getFlags(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getFlags(tablegen_opaque_val);
}
template<typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::setFlags(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, uint32_t debugKind, bool assumeTeamsOversubscription, bool assumeThreadsOversubscription, bool assumeNoThreadState, bool assumeNoNestedParallelism, uint32_t openmpDeviceVersion) {
  return static_cast<const ConcreteOp *>(impl)->setFlags(tablegen_opaque_val, debugKind, assumeTeamsOversubscription, assumeThreadsOversubscription, assumeNoThreadState, assumeNoNestedParallelism, openmpDeviceVersion);
}
template<typename ConcreteOp>
mlir::omp::TargetAttr detail::OffloadModuleInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getTarget(tablegen_opaque_val);
}
template<typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::setTarget(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, llvm::StringRef targetCPU, llvm::StringRef targetFeatures) {
  return static_cast<const ConcreteOp *>(impl)->setTarget(tablegen_opaque_val, targetCPU, targetFeatures);
}
template<typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::setHostIRFilePath(const Concept *impl, ::mlir::Operation *tablegen_opaque_val, std::string hostIRFilePath) {
  return static_cast<const ConcreteOp *>(impl)->setHostIRFilePath(tablegen_opaque_val, hostIRFilePath);
}
template<typename ConcreteOp>
llvm::StringRef detail::OffloadModuleInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getHostIRFilePath(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getHostIRFilePath(tablegen_opaque_val);
}
template<typename ConcreteModel, typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::setIsDevice(::mlir::Operation *tablegen_opaque_val, bool isDevice) const {
(llvm::cast<ConcreteOp>(tablegen_opaque_val))->setAttr(
          mlir::StringAttr::get((llvm::cast<ConcreteOp>(tablegen_opaque_val))->getContext(), llvm::Twine{"omp.is_device"}),
            mlir::omp::IsDeviceAttr::get((llvm::cast<ConcreteOp>(tablegen_opaque_val))->getContext(), isDevice));
}
template<typename ConcreteModel, typename ConcreteOp>
bool detail::OffloadModuleInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::getIsDevice(::mlir::Operation *tablegen_opaque_val) const {
if (Attribute isDevice = (llvm::cast<ConcreteOp>(tablegen_opaque_val))->getAttr("omp.is_device"))
          if (::llvm::isa<mlir::omp::IsDeviceAttr>(isDevice))
            return ::llvm::dyn_cast<IsDeviceAttr>(isDevice).getIsDevice();
        return false;
}
template<typename ConcreteModel, typename ConcreteOp>
mlir::omp::FlagsAttr detail::OffloadModuleInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::getFlags(::mlir::Operation *tablegen_opaque_val) const {
if (Attribute flags = (llvm::cast<ConcreteOp>(tablegen_opaque_val))->getAttr("omp.flags"))
          return flags.dyn_cast_or_null<mlir::omp::FlagsAttr>();
        return nullptr;
}
template<typename ConcreteModel, typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::setFlags(::mlir::Operation *tablegen_opaque_val, uint32_t debugKind, bool assumeTeamsOversubscription, bool assumeThreadsOversubscription, bool assumeNoThreadState, bool assumeNoNestedParallelism, uint32_t openmpDeviceVersion) const {
(llvm::cast<ConcreteOp>(tablegen_opaque_val))->setAttr(("omp." + mlir::omp::FlagsAttr::getMnemonic()).str(),
                  mlir::omp::FlagsAttr::get((llvm::cast<ConcreteOp>(tablegen_opaque_val))->getContext(), debugKind,
                      assumeTeamsOversubscription, assumeThreadsOversubscription,
                      assumeNoThreadState, assumeNoNestedParallelism, openmpDeviceVersion));
}
template<typename ConcreteModel, typename ConcreteOp>
mlir::omp::TargetAttr detail::OffloadModuleInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::getTarget(::mlir::Operation *tablegen_opaque_val) const {
if (Attribute flags = (llvm::cast<ConcreteOp>(tablegen_opaque_val))->getAttr("omp.target"))
          return flags.dyn_cast_or_null<mlir::omp::TargetAttr>();
        return nullptr;
}
template<typename ConcreteModel, typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::setTarget(::mlir::Operation *tablegen_opaque_val, llvm::StringRef targetCPU, llvm::StringRef targetFeatures) const {
if (targetCPU.empty())
          return;
        (llvm::cast<ConcreteOp>(tablegen_opaque_val))->setAttr(("omp." + mlir::omp::TargetAttr::getMnemonic()).str(),
                  mlir::omp::TargetAttr::get((llvm::cast<ConcreteOp>(tablegen_opaque_val))->getContext(),
                                             targetCPU.str(),
                                             targetFeatures.str()));
}
template<typename ConcreteModel, typename ConcreteOp>
void detail::OffloadModuleInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::setHostIRFilePath(::mlir::Operation *tablegen_opaque_val, std::string hostIRFilePath) const {
(llvm::cast<ConcreteOp>(tablegen_opaque_val))->setAttr(
          mlir::StringAttr::get((llvm::cast<ConcreteOp>(tablegen_opaque_val))->getContext(), llvm::Twine{"omp.host_ir_filepath"}),
            mlir::StringAttr::get((llvm::cast<ConcreteOp>(tablegen_opaque_val))->getContext(), hostIRFilePath));
}
template<typename ConcreteModel, typename ConcreteOp>
llvm::StringRef detail::OffloadModuleInterfaceInterfaceTraits::ExternalModel<ConcreteModel, ConcreteOp>::getHostIRFilePath(::mlir::Operation *tablegen_opaque_val) const {
if (Attribute filepath = (llvm::cast<ConcreteOp>(tablegen_opaque_val))->getAttr("omp.host_ir_filepath"))
          if (::llvm::isa<mlir::StringAttr>(filepath))
            return ::llvm::dyn_cast<mlir::StringAttr>(filepath).getValue();
        return {};
}
} // namespace omp
} // namespace mlir
